"""
Tests for the Reddit scraper.

Validates:
  - Normalisation of Reddit posts and comments
  - Handling of deleted items
  - Hierarchy (parent_id) preservation
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from models.schema import FeedbackRecord, SourceEnum
from scrapers.reddit import RedditScraper


class TestRedditNormalise:
    """Tests for Reddit normalisation."""

    def test_normalise_valid_records(
        self, sample_reddit_posts: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Valid posts and comments should be normalised."""
        scraper = RedditScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_reddit_posts)

        # 3rd item is deleted, should be skipped
        assert len(records) == 2

        for record in records:
            assert isinstance(record, FeedbackRecord)
            assert record.source == SourceEnum.REDDIT

    def test_normalise_skips_deleted(
        self, sample_reddit_posts: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Deleted content should be ignored."""
        scraper = RedditScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_reddit_posts)

        assert len(records) == 2
        for record in records:
            assert "[deleted]" not in record.content_raw

    def test_normalise_metadata(
        self, sample_reddit_posts: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Subreddit context and scores should be preserved."""
        scraper = RedditScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_reddit_posts)

        # First item is a post
        assert records[0].platform_metadata.subreddit == "IndianFashionAddicts"
        assert records[0].platform_metadata.score == 45
        assert records[0].platform_metadata.is_comment is False

        # Second item is a comment
        assert records[1].platform_metadata.is_comment is True
        assert records[1].platform_metadata.parent_id == "t3_abc123"
