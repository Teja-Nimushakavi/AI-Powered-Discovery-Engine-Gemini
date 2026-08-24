"""
Unified Feedback Schema for the RAG Discovery Engine.

Defines the canonical data model that all scrapers normalise into.
Matches the architecture specification §4.2 — every feedback record
from any source conforms to this schema before storage.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class SourceEnum(str, Enum):
    """Supported data source platforms."""

    REDDIT = "reddit"
    PLAYSTORE = "playstore"
    APPSTORE = "appstore"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"


class PlatformMetadata(BaseModel):
    """
    Flexible, source-specific metadata fields.

    Each platform can store its own fields here (e.g., star rating for
    app stores, subreddit for Reddit, likes for YouTube).
    """

    rating: float | None = Field(default=None, description="Star rating (1-5) for app store reviews")
    subreddit: str | None = Field(default=None, description="Subreddit name (Reddit)")
    upvotes: int | None = Field(default=None, description="Upvote count (Reddit)")
    downvotes: int | None = Field(default=None, description="Downvote count (Reddit)")
    score: int | None = Field(default=None, description="Net score (Reddit: upvotes - downvotes)")
    likes: int | None = Field(default=None, description="Like count (YouTube, Instagram, Twitter)")
    reply_count: int | None = Field(default=None, description="Number of replies")
    retweet_count: int | None = Field(default=None, description="Retweet count (Twitter)")
    hashtags: list[str] | None = Field(default=None, description="Hashtags (Twitter, Instagram)")
    video_title: str | None = Field(default=None, description="Parent video title (YouTube)")
    video_id: str | None = Field(default=None, description="Parent video ID (YouTube)")
    app_version: str | None = Field(default=None, description="App version (App Store/Play Store)")
    device_info: str | None = Field(default=None, description="Device info (Play Store)")
    review_id: str | None = Field(default=None, description="Platform-native review/post ID")
    parent_id: str | None = Field(default=None, description="Parent post/comment ID for threaded content")
    is_comment: bool = Field(default=False, description="Whether this is a comment vs top-level post")

    model_config = {"extra": "allow"}  # Allow additional platform-specific fields


class FeedbackRecord(BaseModel):
    """
    Unified feedback record schema.

    Every piece of feedback from any source is normalised into this
    structure before being stored. This is the canonical data model
    for the entire pipeline.

    Matches architecture §4.2:
    - feedback_id: UUID v4 (auto-generated)
    - source: Platform origin enum
    - source_url: Direct link to original content
    - author_id_hash: SHA-256 anonymised author identifier
    - content_raw: Original user text
    - content_cleaned: Preprocessed text (basic cleaning in Phase 1)
    - timestamp: Original publication time (ISO-8601)
    - platform_metadata: Source-specific flexible fields
    - ingestion_timestamp: When this record was ingested
    - dedup_fingerprint: SHA-256 of content_cleaned for deduplication
    """

    feedback_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier (UUID v4)",
    )
    source: SourceEnum = Field(description="Platform origin")
    source_url: str = Field(default="", description="Direct link to original content")
    author_id_hash: str = Field(description="SHA-256 hashed author identifier (PII-safe)")
    content_raw: str = Field(description="Original user text, unmodified")
    content_cleaned: str = Field(default="", description="Preprocessed text")
    timestamp: datetime = Field(description="Original publication timestamp")
    platform_metadata: PlatformMetadata = Field(
        default_factory=PlatformMetadata,
        description="Source-specific metadata",
    )
    ingestion_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this record was ingested into the system",
    )
    dedup_fingerprint: str = Field(
        default="",
        description="SHA-256 hash of content_cleaned for deduplication",
    )
    
    # NLP & Enrichment Fields (Phase 3)
    sentiment_scores: dict[str, Any] | None = Field(default=None, description="Sentiment analysis scores")
    purchase_barriers: list[dict[str, Any]] | None = Field(default=None, description="Identified purchase barriers")
    user_behaviours: list[dict[str, Any]] | None = Field(default=None, description="Identified user behaviours")
    relevance: dict[str, Any] | None = Field(default=None, description="Relevance to wishlist-to-purchase conversion")
    user_segment_tags: list[str] | None = Field(default=None, description="Assigned user segment tags")

    @field_validator("author_id_hash", mode="before")
    @classmethod
    def hash_author_id(cls, v: str) -> str:
        """
        Ensure author ID is always SHA-256 hashed.

        If the input doesn't look like a SHA-256 hash (64 hex chars),
        hash it automatically.
        """
        if v and not re.match(r"^[a-f0-9]{64}$", v):
            return hashlib.sha256(v.encode("utf-8")).hexdigest()
        return v

    @model_validator(mode="after")
    def compute_derived_fields(self) -> FeedbackRecord:
        """Compute content_cleaned and dedup_fingerprint if not set."""
        # Basic text cleaning (Phase 1 — minimal; full cleaning in Phase 2)
        if not self.content_cleaned and self.content_raw:
            self.content_cleaned = self._basic_clean(self.content_raw)

        # Compute dedup fingerprint from cleaned content
        if self.content_cleaned and not self.dedup_fingerprint:
            self.dedup_fingerprint = hashlib.sha256(
                self.content_cleaned.encode("utf-8")
            ).hexdigest()

        return self

    @staticmethod
    def _basic_clean(text: str) -> str:
        """
        Basic text cleaning for Phase 1.

        - Strip leading/trailing whitespace
        - Normalise multiple spaces/newlines
        - Strip null bytes

        Full preprocessing (HTML strip, Unicode normalisation, emoji
        handling, URL extraction, PII redaction) is deferred to Phase 2.
        """
        text = text.strip()
        text = text.replace("\x00", "")
        text = re.sub(r"\s+", " ", text)
        return text

    def to_jsonl_dict(self) -> dict[str, Any]:
        """
        Serialise to a JSON-compatible dict for JSONL output.

        Converts datetime fields to ISO-8601 strings and enums to values.
        """
        data = self.model_dump()
        data["source"] = self.source.value
        data["timestamp"] = self.timestamp.isoformat()
        data["ingestion_timestamp"] = self.ingestion_timestamp.isoformat()
        return data


def hash_author_id(raw_id: str) -> str:
    """
    Utility function to SHA-256 hash an author identifier.

    Use this in scrapers before constructing a FeedbackRecord if you
    want explicit control over hashing.
    """
    return hashlib.sha256(raw_id.encode("utf-8")).hexdigest()


def validate_records(records: list[dict[str, Any]]) -> tuple[list[FeedbackRecord], list[dict[str, Any]]]:
    """
    Validate a batch of raw record dicts against the FeedbackRecord schema.

    Returns:
        Tuple of (valid_records, invalid_records_with_errors)
    """
    valid: list[FeedbackRecord] = []
    invalid: list[dict[str, Any]] = []

    for record in records:
        try:
            valid.append(FeedbackRecord(**record))
        except Exception as e:
            invalid.append({"record": record, "error": str(e)})

    return valid, invalid
