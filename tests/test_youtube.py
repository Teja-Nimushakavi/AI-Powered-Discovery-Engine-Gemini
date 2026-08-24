"""
Tests for the YouTube scraper.

Validates:
  - Normalisation of YouTube comments
  - Video context preservation
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from models.schema import FeedbackRecord, SourceEnum
from scrapers.youtube import YouTubeScraper


class TestYouTubeNormalise:
    """Tests for YouTube normalisation."""

    def test_normalise_valid_records(
        self, sample_youtube_comments: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Valid comments should be normalised."""
        scraper = YouTubeScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_youtube_comments)

        assert len(records) == 2

        for record in records:
            assert isinstance(record, FeedbackRecord)
            assert record.source == SourceEnum.YOUTUBE

    def test_normalise_metadata(
        self, sample_youtube_comments: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Video context and likes should be preserved."""
        scraper = YouTubeScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_youtube_comments)

        assert records[0].platform_metadata.video_title == "HUGE Myntra Haul 2024 | Try On | Worth it?"
        assert records[0].platform_metadata.video_id == "abc123xyz"
        assert records[0].platform_metadata.likes == 34
        assert records[0].platform_metadata.is_comment is True
