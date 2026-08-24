"""
Google Play Store Scraper for Myntra App Reviews.

Fetches reviews for the Myntra Android app (com.myntra.android) using
the google-play-scraper library. Targets ≥ 1,500 authentic reviews.

Features:
  - Paginated fetching with configurable batch sizes
  - Sorts by newest first to get recent feedback
  - Extracts star rating, review text, date, device info, app version
  - Normalises to unified FeedbackRecord schema
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from scrapers.base import BaseScraper
from models.schema import FeedbackRecord, PlatformMetadata, SourceEnum

logger = logging.getLogger(__name__)

# Myntra Android app package ID
MYNTRA_PACKAGE_ID = "com.myntra.android"

# Batch size for paginated fetching
FETCH_BATCH_SIZE = 200


class PlayStoreScraper(BaseScraper):
    """
    Scraper for Google Play Store reviews of the Myntra Android app.

    Uses the google-play-scraper library which accesses public Play Store
    data without requiring API keys.
    """

    SOURCE_NAME = "playstore"

    def __init__(
        self,
        max_records: int | None = None,
        app_id: str = MYNTRA_PACKAGE_ID,
        **kwargs: Any,
    ) -> None:
        super().__init__(max_records=max_records or 1500, **kwargs)
        self.app_id = app_id

    def scrape(self) -> list[dict[str, Any]]:
        """
        Fetch reviews from Google Play Store.

        Uses continuation tokens for pagination to fetch beyond the
        initial batch. Sorts by newest to capture recent feedback.
        """
        try:
            from google_play_scraper import Sort, reviews
        except ImportError:
            self._logger.error(
                "google-play-scraper not installed. Run: pip install google-play-scraper"
            )
            return []

        all_reviews: list[dict[str, Any]] = []
        continuation_token = None
        fetched = 0

        self._logger.info(
            "Fetching up to %d reviews for app '%s'",
            self.max_records,
            self.app_id,
        )

        while fetched < self.max_records:
            batch_size = min(FETCH_BATCH_SIZE, self.max_records - fetched)

            try:
                result, continuation_token = self._retry_with_backoff(
                    reviews,
                    self.app_id,
                    lang="en",
                    country="in",
                    sort=Sort.NEWEST,
                    count=batch_size,
                    continuation_token=continuation_token,
                )
            except Exception as e:
                self._logger.error("Failed to fetch reviews: %s", e)
                break

            if not result:
                self._logger.info("No more reviews available")
                break

            all_reviews.extend(result)
            fetched += len(result)
            self._logger.info(
                "Fetched %d/%d reviews (batch: %d)",
                fetched,
                self.max_records,
                len(result),
            )

            if continuation_token is None:
                break

            self._rate_limit()

        self._logger.info("Total Play Store reviews fetched: %d", len(all_reviews))
        return all_reviews

    def normalise(self, raw_records: list[dict[str, Any]]) -> list[FeedbackRecord]:
        """
        Convert Play Store review dicts to FeedbackRecord instances.

        Play Store review dict fields:
          - reviewId, userName, content, score, thumbsUpCount,
            reviewCreatedVersion, at, replyContent, repliedAt
        """
        records: list[FeedbackRecord] = []

        for raw in raw_records:
            try:
                content = raw.get("content", "")
                if not content or not content.strip():
                    continue  # Skip empty reviews

                # Parse timestamp
                review_date = raw.get("at")
                if isinstance(review_date, datetime):
                    timestamp = review_date.replace(tzinfo=timezone.utc) if review_date.tzinfo is None else review_date
                else:
                    timestamp = datetime.now(timezone.utc)

                # Build platform metadata
                metadata = PlatformMetadata(
                    rating=float(raw.get("score", 0)),
                    review_id=raw.get("reviewId", ""),
                    app_version=raw.get("reviewCreatedVersion", ""),
                    likes=raw.get("thumbsUpCount", 0),
                )

                # Construct source URL
                source_url = (
                    f"https://play.google.com/store/apps/details"
                    f"?id={self.app_id}&reviewId={raw.get('reviewId', '')}"
                )

                # Build FeedbackRecord — author_id_hash auto-hashes
                record = FeedbackRecord(
                    source=SourceEnum.PLAYSTORE,
                    source_url=source_url,
                    author_id_hash=raw.get("userName", "anonymous_playstore"),
                    content_raw=content,
                    timestamp=timestamp,
                    platform_metadata=metadata,
                )
                records.append(record)

            except Exception as e:
                self._logger.warning(
                    "Failed to normalise Play Store review: %s (review_id=%s)",
                    e,
                    raw.get("reviewId", "unknown"),
                )

        return records
