"""
Tests for the App Store scraper.

Validates:
  - Normalisation of App Store reviews to FeedbackRecord
  - Combination of title and body
  - Schema compliance
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from models.schema import FeedbackRecord, SourceEnum
from scrapers.appstore import AppStoreScraper


class TestAppStoreNormalise:
    """Tests for App Store review normalisation."""

    def test_normalise_valid_reviews(
        self, sample_appstore_reviews: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Valid reviews should be normalised to FeedbackRecords."""
        scraper = AppStoreScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_appstore_reviews)

        assert len(records) == 2

        for record in records:
            assert isinstance(record, FeedbackRecord)
            assert record.source == SourceEnum.APPSTORE
            assert record.content_raw
            assert record.author_id_hash
            assert record.feedback_id
            assert record.dedup_fingerprint

    def test_normalise_combines_title_and_review(
        self, sample_appstore_reviews: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """App store title and body should be combined into content_raw."""
        scraper = AppStoreScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_appstore_reviews)

        # "Good app but needs improvement" is title
        # "Colors shown..." is body
        assert "Good app but needs improvement: Colors shown" in records[0].content_raw

    def test_normalise_extracts_rating(
        self, sample_appstore_reviews: list[dict[str, Any]], tmp_output_dir: Path
    ) -> None:
        """Star ratings should be extracted to platform_metadata."""
        scraper = AppStoreScraper(max_records=10, output_dir=tmp_output_dir)
        records = scraper.normalise(sample_appstore_reviews)

        assert records[0].platform_metadata.rating == 3.0
        assert records[1].platform_metadata.rating == 5.0
