"""
Instagram Scraper for Myntra-related Posts and Comments.

Fetches public posts and comments mentioning Myntra from Instagram.
Targets ≥ 400 authentic posts+comments.

Primary method: Instaloader (public scraping, no API key required)
Fallback: Instagram Graph API (requires Facebook Developer account)

Features:
  - Scrapes posts with #myntra hashtag
  - Extracts captions and comments
  - Handles public profile and hashtag pages
  - Normalises to unified FeedbackRecord schema
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from scrapers.base import BaseScraper
from models.schema import FeedbackRecord, PlatformMetadata, SourceEnum
from config.settings import get_settings

logger = logging.getLogger(__name__)

# Hashtags and profiles to target
TARGET_HASHTAGS = [
    "myntra",
    "myntrahaul",
    "myntrareview",
    "myntra_fashion",
    "myntrahaul2024",
    "myntraeors",
    "myntrasale",
]

TARGET_PROFILES = [
    "myntra",
]


class InstagramScraper(BaseScraper):
    """
    Scraper for Instagram posts and comments related to Myntra.

    Uses Instaloader by default for public scraping without API keys.
    Can optionally use Instagram Graph API if credentials are configured.
    """

    SOURCE_NAME = "instagram"

    def __init__(
        self,
        max_records: int | None = None,
        hashtags: list[str] | None = None,
        profiles: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(max_records=max_records or 400, rate_limit_delay=3.0, **kwargs)
        self.hashtags = hashtags or TARGET_HASHTAGS
        self.profiles = profiles or TARGET_PROFILES

    def scrape(self) -> list[dict[str, Any]]:
        """
        Fetch Myntra-related Instagram posts and comments.

        Uses Instaloader for public scraping by default. Falls back
        to Graph API if configured and Instaloader fails.
        """
        settings = get_settings()

        if settings.instagram_use_instaloader:
            records = self._scrape_with_instaloader()
        else:
            records = self._scrape_with_graph_api()

        if not records:
            self._logger.warning(
                "No records from primary method, trying fallback..."
            )
            # Try the other method as fallback
            if settings.instagram_use_instaloader:
                records = self._scrape_with_graph_api()
            else:
                records = self._scrape_with_instaloader()

        return records

    def _scrape_with_instaloader(self) -> list[dict[str, Any]]:
        """Scrape Instagram using Instaloader (no API key needed)."""
        try:
            import instaloader
        except ImportError:
            self._logger.error(
                "instaloader not installed. Run: pip install instaloader"
            )
            return []

        loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=True,
            save_metadata=False,
            compress_json=False,
        )

        all_records: list[dict[str, Any]] = []
        seen_shortcodes: set[str] = set()

        for hashtag in self.hashtags:
            if len(all_records) >= self.max_records:
                break

            self._logger.info("Scraping Instagram hashtag: #%s", hashtag)

            try:
                hashtag_obj = instaloader.Hashtag.from_name(
                    loader.context, hashtag
                )

                post_count = 0
                for post in hashtag_obj.get_posts():
                    if len(all_records) >= self.max_records:
                        break
                    if post_count >= 50:  # Limit posts per hashtag
                        break

                    if post.shortcode in seen_shortcodes:
                        continue
                    seen_shortcodes.add(post.shortcode)

                    # Add the post caption
                    if post.caption:
                        all_records.append({
                            "type": "post",
                            "shortcode": post.shortcode,
                            "caption": post.caption or "",
                            "author": post.owner_username or "",
                            "likes": post.likes,
                            "comments_count": post.comments,
                            "timestamp": post.date_utc.isoformat() if post.date_utc else "",
                            "hashtags": list(post.caption_hashtags) if post.caption_hashtags else [],
                            "url": f"https://www.instagram.com/p/{post.shortcode}/",
                            "is_comment": False,
                        })

                    # Add comments on the post
                    try:
                        for comment in post.get_comments():
                            if len(all_records) >= self.max_records:
                                break
                            all_records.append({
                                "type": "comment",
                                "shortcode": post.shortcode,
                                "caption": comment.text or "",
                                "author": comment.owner.username if comment.owner else "",
                                "likes": comment.likes_count if hasattr(comment, "likes_count") else 0,
                                "timestamp": comment.created_at_utc.isoformat() if comment.created_at_utc else "",
                                "url": f"https://www.instagram.com/p/{post.shortcode}/",
                                "parent_id": post.shortcode,
                                "is_comment": True,
                            })
                    except Exception as e:
                        self._logger.warning(
                            "Failed to fetch comments for post %s: %s",
                            post.shortcode,
                            e,
                        )

                    post_count += 1
                    self._rate_limit()

            except Exception as e:
                self._logger.warning(
                    "Failed to scrape hashtag #%s: %s",
                    hashtag,
                    e,
                )

        self._logger.info(
            "Total Instagram records via Instaloader: %d", len(all_records)
        )
        return all_records[: self.max_records]

    def _scrape_with_graph_api(self) -> list[dict[str, Any]]:
        """
        Scrape Instagram using the Graph API.

        Requires INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID
        to be configured in .env.
        """
        import requests

        settings = get_settings()

        if not settings.instagram_access_token or not settings.instagram_business_account_id:
            self._logger.warning(
                "Instagram Graph API credentials not configured. "
                "Set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID in .env"
            )
            return []

        all_records: list[dict[str, Any]] = []
        base_url = "https://graph.facebook.com/v18.0"

        for hashtag_name in self.hashtags[:3]:  # Limit to 3 hashtags for API quota
            if len(all_records) >= self.max_records:
                break

            try:
                # Step 1: Get hashtag ID
                hashtag_resp = requests.get(
                    f"{base_url}/ig_hashtag_search",
                    params={
                        "user_id": settings.instagram_business_account_id,
                        "q": hashtag_name,
                        "access_token": settings.instagram_access_token,
                    },
                    timeout=30,
                )
                hashtag_resp.raise_for_status()
                hashtag_data = hashtag_resp.json()

                if not hashtag_data.get("data"):
                    continue

                hashtag_id = hashtag_data["data"][0]["id"]

                # Step 2: Get recent media for hashtag
                media_resp = requests.get(
                    f"{base_url}/{hashtag_id}/recent_media",
                    params={
                        "user_id": settings.instagram_business_account_id,
                        "fields": "id,caption,timestamp,like_count,comments_count,permalink",
                        "access_token": settings.instagram_access_token,
                    },
                    timeout=30,
                )
                media_resp.raise_for_status()
                media_data = media_resp.json()

                for post in media_data.get("data", []):
                    if len(all_records) >= self.max_records:
                        break

                    all_records.append({
                        "type": "post",
                        "shortcode": post.get("id", ""),
                        "caption": post.get("caption", ""),
                        "author": "",
                        "likes": post.get("like_count", 0),
                        "comments_count": post.get("comments_count", 0),
                        "timestamp": post.get("timestamp", ""),
                        "url": post.get("permalink", ""),
                        "is_comment": False,
                    })

                self._rate_limit()

            except Exception as e:
                self._logger.warning(
                    "Graph API failed for hashtag #%s: %s",
                    hashtag_name,
                    e,
                )

        self._logger.info(
            "Total Instagram records via Graph API: %d", len(all_records)
        )
        return all_records

    def normalise(self, raw_records: list[dict[str, Any]]) -> list[FeedbackRecord]:
        """Convert Instagram post/comment dicts to FeedbackRecord instances."""
        records: list[FeedbackRecord] = []

        for raw in raw_records:
            try:
                content = raw.get("caption", "")
                if not content or not content.strip():
                    continue

                # Parse timestamp
                timestamp_str = raw.get("timestamp", "")
                try:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    timestamp = datetime.now(timezone.utc)

                # Build platform metadata
                metadata = PlatformMetadata(
                    likes=raw.get("likes", 0),
                    reply_count=raw.get("comments_count"),
                    hashtags=raw.get("hashtags", []),
                    review_id=raw.get("shortcode", ""),
                    parent_id=raw.get("parent_id"),
                    is_comment=raw.get("is_comment", False),
                )

                record = FeedbackRecord(
                    source=SourceEnum.INSTAGRAM,
                    source_url=raw.get("url", ""),
                    author_id_hash=raw.get("author", "anonymous_instagram"),
                    content_raw=content,
                    timestamp=timestamp,
                    platform_metadata=metadata,
                )
                records.append(record)

            except Exception as e:
                self._logger.warning(
                    "Failed to normalise Instagram record: %s",
                    e,
                )

        return records
