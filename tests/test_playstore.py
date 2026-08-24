"""
Tests for the Play Store scraper.

Validates:
  - Normalisation of Play Store reviews to FeedbackRecord
  - Correct handling of empty reviews (skipped)
  - Schema compliance of normalised records
  - JSONL output
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from models.schema import FeedbackRecord, SourceEnum
from scrapers.playstore import PlayStoreScraper


class TestPlayStoreNormalise:
    """Tests for Play Store review normalisation."""

    def test_normalise_valid_reviews(
        self, sample_playstore_reviews: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Valid reviews should be normalised to FeedbackRecords."""
        scraper = PlayStoreScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_playstore_reviews)

        # Should skip the empty review (4th item)
        assert len(records) == 3

        for record in records:
            assert isinstance(record, FeedbackRecord)
            assert record.source == SourceEnum.PLAYSTORE
            assert record.content_raw
            assert record.author_id_hash
            assert record.feedback_id
            assert record.dedup_fingerprint

    def test_normalise_preserves_content(
        self, sample_playstore_reviews: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Original review content should be preserved in content_raw."""
        scraper = PlayStoreScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_playstore_reviews)

        assert "sizing is always off" in records[0].content_raw
        assert "EORS sale" in records[1].content_raw

    def test_normalise_extracts_rating(
        self, sample_playstore_reviews: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Star ratings should be extracted to platform_metadata."""
        scraper = PlayStoreScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_playstore_reviews)

        assert records[0].platform_metadata.rating == 3.0
        assert records[1].platform_metadata.rating == 5.0
        assert records[2].platform_metadata.rating == 1.0

    def test_normalise_skips_empty_reviews(
        self, sample_playstore_reviews: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Reviews with empty content should be skipped."""
        scraper = PlayStoreScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_playstore_reviews)

        # 4th review has empty content — should be excluded
        assert len(records) == 3
        for record in records:
            assert record.content_raw.strip() != ""

    def test_normalise_source_url(
        self, sample_playstore_reviews: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Source URLs should point to Play Store."""
        scraper = PlayStoreScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_playstore_reviews)

        for record in records:
            assert "play.google.com" in record.source_url

    def test_save_jsonl(
        self, sample_playstore_reviews: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Records should be saveable as JSONL."""
        scraper = PlayStoreScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_playstore_reviews)
        output_path = scraper.save(records, filename="test_playstore.jsonl")

        assert output_path.exists()
        lines = output_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3
