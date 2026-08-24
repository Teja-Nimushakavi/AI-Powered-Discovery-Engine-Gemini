"""
Apple App Store Scraper for Myntra iOS App Reviews.

Fetches reviews for the Myntra iOS app using the app-store-scraper
library. Targets ≥ 800 authentic reviews. Region-aware fetching
focused on the India App Store.

Features:
  - Region-aware fetching (India primary, US/UK fallback)
  - Extracts star rating, review text, date, app version
  - Normalises to unified FeedbackRecord schema
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from scrapers.base import BaseScraper
from models.schema import FeedbackRecord, PlatformMetadata, SourceEnum

logger = logging.getLogger(__name__)

# Myntra iOS App details
MYNTRA_APP_NAME = "myntra"
MYNTRA_APP_ID = 907394059  # Myntra app ID on the App Store


class AppStoreScraper(BaseScraper):
    """
    Scraper for Apple App Store reviews of the Myntra iOS app.

    Uses the app-store-scraper library which accesses public App Store
    RSS feeds without requiring API keys.
    """

    SOURCE_NAME = "appstore"

    def __init__(
        self,
        max_records: int | None = None,
        app_name: str = MYNTRA_APP_NAME,
        app_id: int = MYNTRA_APP_ID,
        countries: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(max_records=max_records or 800, **kwargs)
        self.app_name = app_name
        self.app_id = app_id
        # Primary: India; fallback to other English-speaking markets
        self.countries = countries or ["in", "us", "gb"]

    def scrape(self) -> list[dict[str, Any]]:
        """
        Fetch reviews from Apple App Store across multiple regions.

        Iterates through configured countries to maximize review volume.
        India (in) is the primary market for Myntra.
        """
        try:
            from app_store_scraper import AppStore
        except ImportError:
            self._logger.error(
                "app-store-scraper not installed. Run: pip install app-store-scraper"
            )
            return []

        all_reviews: list[dict[str, Any]] = []
        seen_ids: set[str] = set()  # Prevent cross-region duplicates

        for country in self.countries:
            if len(all_reviews) >= self.max_records:
                break

            remaining = self.max_records - len(all_reviews)
            self._logger.info(
                "Fetching up to %d reviews from App Store (country=%s)",
                remaining,
                country,
            )

            try:
                app = AppStore(
                    country=country,
                    app_name=self.app_name,
                    app_id=self.app_id,
                )

                self._retry_with_backoff(
                    app.review,
                    how_many=remaining,
                )

                for review in app.reviews:
                    # Deduplicate across regions using review title + date
                    review_key = f"{review.get('title', '')}_{review.get('date', '')}"
                    if review_key not in seen_ids:
                        seen_ids.add(review_key)
                        review["_country"] = country
                        all_reviews.append(review)

                self._logger.info(
                    "Fetched %d reviews from App Store (country=%s), total: %d",
                    len(app.reviews),
                    country,
                    len(all_reviews),
                )

            except Exception as e:
                self._logger.warning(
                    "Failed to fetch App Store reviews for country=%s: %s",
                    country,
                    e,
                )

            self._rate_limit()

        self._logger.info("Total App Store reviews fetched: %d", len(all_reviews))
        return all_reviews[: self.max_records]

    def normalise(self, raw_records: list[dict[str, Any]]) -> list[FeedbackRecord]:
        """
        Convert App Store review dicts to FeedbackRecord instances.

        App Store review dict fields:
          - title, review, rating, date, userName, isEdited,
            developerResponse (dict with body, modified)
        """
        records: list[FeedbackRecord] = []

        for raw in raw_records:
            try:
                # Combine title and review body
                title = raw.get("title", "")
                review_body = raw.get("review", "")
                content = f"{title}: {review_body}" if title else review_body

                if not content or not content.strip():
                    continue

                # Parse timestamp
                review_date = raw.get("date")
                if isinstance(review_date, datetime):
                    timestamp = review_date.replace(tzinfo=timezone.utc) if review_date.tzinfo is None else review_date
                else:
                    timestamp = datetime.now(timezone.utc)

                # Build platform metadata
                metadata = PlatformMetadata(
                    rating=float(raw.get("rating", 0)),
                    app_version=str(raw.get("isEdited", "")),
                    review_id=f"appstore_{raw.get('title', '')[:30]}_{raw.get('_country', 'in')}",
                )

                # Source URL — App Store doesn't have per-review URLs
                source_url = (
                    f"https://apps.apple.com/{raw.get('_country', 'in')}"
                    f"/app/{self.app_name}/id{self.app_id}"
                )

                record = FeedbackRecord(
                    source=SourceEnum.APPSTORE,
                    source_url=source_url,
                    author_id_hash=raw.get("userName", "anonymous_appstore"),
                    content_raw=content,
                    timestamp=timestamp,
                    platform_metadata=metadata,
                )
                records.append(record)

            except Exception as e:
                self._logger.warning(
                    "Failed to normalise App Store review: %s",
                    e,
                )

        return records
