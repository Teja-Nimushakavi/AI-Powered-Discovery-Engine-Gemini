"""
Tests for the Twitter/X scraper.

Validates:
  - Normalisation of tweets
  - Hashtag and metrics extraction
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from models.schema import FeedbackRecord, SourceEnum
from scrapers.twitter import TwitterScraper


class TestTwitterNormalise:
    """Tests for Twitter normalisation."""

    def test_normalise_valid_records(
        self, sample_twitter_tweets: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Valid tweets should be normalised."""
        scraper = TwitterScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_twitter_tweets)

        assert len(records) == 2

        for record in records:
            assert isinstance(record, FeedbackRecord)
            assert record.source == SourceEnum.TWITTER

    def test_normalise_metadata(
        self, sample_twitter_tweets: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Engagement metrics and hashtags should be preserved."""
        scraper = TwitterScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_twitter_tweets)

        assert records[0].platform_metadata.likes == 23
        assert records[0].platform_metadata.retweet_count == 5
        assert "colormismatch" in records[0].platform_metadata.hashtags  # type: ignore[operator]
