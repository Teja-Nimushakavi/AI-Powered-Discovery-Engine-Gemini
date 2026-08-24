"""
Tests for the unified FeedbackRecord schema.

Validates:
  - Schema creation with valid data
  - Auto-generation of UUID, dedup fingerprint
  - Auto-hashing of author IDs
  - Basic text cleaning
  - Schema validation (invalid data rejected)
  - JSONL serialisation
  - Batch validation utility
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone

import pytest

from models.schema import (
    FeedbackRecord,
    PlatformMetadata,
    SourceEnum,
    hash_author_id,
    validate_records,
)


class TestSourceEnum:
    """Tests for the SourceEnum."""

    def test_all_sources_exist(self) -> None:
        """All 6 data sources must be defined."""
        sources = [e.value for e in SourceEnum]
        assert "reddit" in sources
        assert "playstore" in sources
        assert "appstore" in sources
        assert "youtube" in sources
        assert "twitter" in sources
        assert "instagram" in sources
        assert len(sources) == 6

    def test_source_values_are_lowercase(self) -> None:
        """Source values must be lowercase strings."""
        for source in SourceEnum:
            assert source.value == source.value.lower()


class TestPlatformMetadata:
    """Tests for the PlatformMetadata model."""

    def test_empty_metadata(self) -> None:
        """Empty metadata should be valid."""
        meta = PlatformMetadata()
        assert meta.rating is None
        assert meta.subreddit is None

    def test_playstore_metadata(self) -> None:
        """Play Store metadata with rating and review ID."""
        meta = PlatformMetadata(
            rating=4.5,
            review_id="gp_123",
            app_version="4.2.1",
            likes=15,
        )
        assert meta.rating == 4.5
        assert meta.review_id == "gp_123"

    def test_reddit_metadata(self) -> None:
        """Reddit metadata with subreddit and score."""
        meta = PlatformMetadata(
            subreddit="IndianFashionAddicts",
            score=42,
            upvotes=42,
            is_comment=True,
        )
        assert meta.subreddit == "IndianFashionAddicts"
        assert meta.score == 42

    def test_extra_fields_allowed(self) -> None:
        """Extra fields should be accepted (Config extra='allow')."""
        meta = PlatformMetadata(custom_field="custom_value")
        assert meta.custom_field == "custom_value"  # type: ignore[attr-defined]


class TestFeedbackRecord:
    """Tests for the FeedbackRecord model."""

    def test_create_valid_record(self) -> None:
        """A valid record should be created successfully."""
        record = FeedbackRecord(
            source=SourceEnum.PLAYSTORE,
            source_url="https://play.google.com/store/apps/details?id=com.myntra.android",
            author_id_hash="raw_user_id",
            content_raw="Great app but sizing is off!",
            timestamp=datetime(2024, 6, 15, tzinfo=timezone.utc),
        )
        assert record.source == SourceEnum.PLAYSTORE
        assert record.content_raw == "Great app but sizing is off!"
        assert record.feedback_id  # UUID auto-generated
        assert record.ingestion_timestamp  # Auto-set
        assert record.content_cleaned  # Auto-computed
        assert record.dedup_fingerprint  # Auto-computed

    def test_uuid_auto_generated(self) -> None:
        """Each record should get a unique UUID."""
        r1 = FeedbackRecord(
            source=SourceEnum.REDDIT,
            author_id_hash="user1",
            content_raw="Test content 1",
            timestamp=datetime.now(timezone.utc),
        )
        r2 = FeedbackRecord(
            source=SourceEnum.REDDIT,
            author_id_hash="user2",
            content_raw="Test content 2",
            timestamp=datetime.now(timezone.utc),
        )
        assert r1.feedback_id != r2.feedback_id
        # Verify UUID format
        uuid_pattern = re.compile(
            r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
        )
        assert uuid_pattern.match(r1.feedback_id)

    def test_author_id_auto_hashed(self) -> None:
        """Raw author IDs should be SHA-256 hashed automatically."""
        record = FeedbackRecord(
            source=SourceEnum.TWITTER,
            author_id_hash="plaintext_username",
            content_raw="Some tweet",
            timestamp=datetime.now(timezone.utc),
        )
        expected_hash = hashlib.sha256(b"plaintext_username").hexdigest()
        assert record.author_id_hash == expected_hash
        assert len(record.author_id_hash) == 64

    def test_already_hashed_id_unchanged(self) -> None:
        """A pre-hashed author ID (64 hex chars) should not be double-hashed."""
        pre_hashed = hashlib.sha256(b"some_user").hexdigest()
        record = FeedbackRecord(
            source=SourceEnum.YOUTUBE,
            author_id_hash=pre_hashed,
            content_raw="Comment",
            timestamp=datetime.now(timezone.utc),
        )
        assert record.author_id_hash == pre_hashed

    def test_content_cleaned_auto_computed(self) -> None:
        """Basic cleaning should strip whitespace and normalise spaces."""
        record = FeedbackRecord(
            source=SourceEnum.APPSTORE,
            author_id_hash="user",
            content_raw="  Too   many    spaces   and\n\nnewlines  ",
            timestamp=datetime.now(timezone.utc),
        )
        assert record.content_cleaned == "Too many spaces and newlines"

    def test_dedup_fingerprint_computed(self) -> None:
        """Dedup fingerprint should be SHA-256 of content_cleaned."""
        record = FeedbackRecord(
            source=SourceEnum.INSTAGRAM,
            author_id_hash="user",
            content_raw="Test content for dedup",
            timestamp=datetime.now(timezone.utc),
        )
        expected = hashlib.sha256(
            record.content_cleaned.encode("utf-8")
        ).hexdigest()
        assert record.dedup_fingerprint == expected

    def test_identical_content_same_fingerprint(self) -> None:
        """Two records with identical content should have the same fingerprint."""
        r1 = FeedbackRecord(
            source=SourceEnum.PLAYSTORE,
            author_id_hash="user1",
            content_raw="Same content here",
            timestamp=datetime.now(timezone.utc),
        )
        r2 = FeedbackRecord(
            source=SourceEnum.REDDIT,
            author_id_hash="user2",
            content_raw="Same content here",
            timestamp=datetime.now(timezone.utc),
        )
        assert r1.dedup_fingerprint == r2.dedup_fingerprint

    def test_to_jsonl_dict(self) -> None:
        """JSONL dict should be JSON-serialisable with ISO timestamps."""
        record = FeedbackRecord(
            source=SourceEnum.PLAYSTORE,
            author_id_hash="user",
            content_raw="Test",
            timestamp=datetime(2024, 6, 15, 10, 0, 0, tzinfo=timezone.utc),
        )
        d = record.to_jsonl_dict()

        # Should be JSON-serialisable
        json_str = json.dumps(d)
        assert json_str

        # Source should be string value
        assert d["source"] == "playstore"

        # Timestamps should be ISO strings
        assert isinstance(d["timestamp"], str)
        assert "2024-06-15" in d["timestamp"]

    def test_missing_required_fields_raises(self) -> None:
        """Missing required fields should raise validation error."""
        with pytest.raises(Exception):
            FeedbackRecord(
                source=SourceEnum.REDDIT,
                # Missing: author_id_hash, content_raw, timestamp
            )

    def test_invalid_source_raises(self) -> None:
        """Invalid source value should raise validation error."""
        with pytest.raises(Exception):
            FeedbackRecord(
                source="invalid_source",  # type: ignore[arg-type]
                author_id_hash="user",
                content_raw="Test",
                timestamp=datetime.now(timezone.utc),
            )

    def test_with_platform_metadata(self) -> None:
        """Record with full platform metadata should work."""
        meta = PlatformMetadata(
            rating=4.0,
            subreddit="IndianFashionAddicts",
            likes=25,
            hashtags=["myntra", "haul"],
        )
        record = FeedbackRecord(
            source=SourceEnum.REDDIT,
            author_id_hash="user",
            content_raw="Great haul!",
            timestamp=datetime.now(timezone.utc),
            platform_metadata=meta,
        )
        assert record.platform_metadata.rating == 4.0
        assert record.platform_metadata.subreddit == "IndianFashionAddicts"


class TestUtilityFunctions:
    """Tests for schema utility functions."""

    def test_hash_author_id(self) -> None:
        """hash_author_id should return consistent SHA-256 hashes."""
        h1 = hash_author_id("test_user")
        h2 = hash_author_id("test_user")
        assert h1 == h2
        assert len(h1) == 64

    def test_validate_records_all_valid(self) -> None:
        """validate_records should return all valid records."""
        records = [
            {
                "source": "reddit",
                "author_id_hash": "user1",
                "content_raw": "Content 1",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            {
                "source": "playstore",
                "author_id_hash": "user2",
                "content_raw": "Content 2",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ]
        valid, invalid = validate_records(records)
        assert len(valid) == 2
        assert len(invalid) == 0

    def test_validate_records_mixed(self) -> None:
        """validate_records should separate valid and invalid records."""
        records = [
            {
                "source": "reddit",
                "author_id_hash": "user1",
                "content_raw": "Valid content",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            {
                "source": "invalid_source",
                "author_id_hash": "user2",
                "content_raw": "Invalid source",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ]
        valid, invalid = validate_records(records)
        assert len(valid) == 1
        assert len(invalid) == 1
        assert "error" in invalid[0]
