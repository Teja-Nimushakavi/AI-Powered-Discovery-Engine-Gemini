"""
Tests for the Instagram scraper.

Validates:
  - Normalisation of posts and comments
  - Hashtag and metrics extraction
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from models.schema import FeedbackRecord, SourceEnum
from scrapers.instagram import InstagramScraper


class TestInstagramNormalise:
    """Tests for Instagram normalisation."""

    def test_normalise_valid_records(
        self, sample_instagram_posts: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Valid posts and comments should be normalised."""
        scraper = InstagramScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_instagram_posts)

        assert len(records) == 2

        for record in records:
            assert isinstance(record, FeedbackRecord)
            assert record.source == SourceEnum.INSTAGRAM

    def test_normalise_metadata(
        self, sample_instagram_posts: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Engagement metrics and hierarchy should be preserved."""
        scraper = InstagramScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_instagram_posts)

        # Post
        assert records[0].platform_metadata.likes == 234
        assert records[0].platform_metadata.is_comment is False
        assert "myntrahaul" in records[0].platform_metadata.hashtags  # type: ignore[operator]

        # Comment
        assert records[1].platform_metadata.is_comment is True
        assert records[1].platform_metadata.parent_id == "ig_001"
