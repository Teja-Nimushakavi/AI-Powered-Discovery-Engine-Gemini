"""
YouTube Scraper for Myntra Haul/Review Video Comments.

Fetches comments from YouTube videos related to Myntra hauls and
reviews using the YouTube Data API v3. Targets ≥ 800 authentic comments.

Features:
  - Searches for Myntra haul/review/try-on videos
  - Fetches comment threads from relevant videos (50+ videos)
  - Extracts comment text, likes, replies, video context
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

# Search queries to find Myntra-related videos
VIDEO_SEARCH_QUERIES = [
    "myntra haul",
    "myntra try on haul",
    "myntra review",
    "myntra shopping haul",
    "myntra sale haul",
    "myntra EORS haul",
    "myntra outfit review",
    "myntra fashion haul",
    "myntra unboxing",
    "myntra vs ajio",
]

# Maximum comments per video to avoid API quota exhaustion
MAX_COMMENTS_PER_VIDEO = 100


class YouTubeScraper(BaseScraper):
    """
    Scraper for YouTube comments on Myntra haul/review videos.

    Uses the YouTube Data API v3 to search for relevant videos and
    then fetch their comment threads. Requires a YouTube API key.
    """

    SOURCE_NAME = "youtube"

    def __init__(
        self,
        max_records: int | None = None,
        search_queries: list[str] | None = None,
        max_videos: int = 60,
        max_comments_per_video: int = MAX_COMMENTS_PER_VIDEO,
        **kwargs: Any,
    ) -> None:
        super().__init__(max_records=max_records or 800, rate_limit_delay=1.5, **kwargs)
        self.search_queries = search_queries or VIDEO_SEARCH_QUERIES
        self.max_videos = max_videos
        self.max_comments_per_video = max_comments_per_video

    def _get_youtube_client(self) -> Any:
        """Create and return a YouTube API client."""
        try:
            from googleapiclient.discovery import build
        except ImportError:
            self._logger.error(
                "google-api-python-client not installed. "
                "Run: pip install google-api-python-client"
            )
            raise

        settings = get_settings()

        if not settings.youtube_api_key:
            self._logger.error(
                "YouTube API key not configured. "
                "Set YOUTUBE_API_KEY in .env"
            )
            raise ValueError("Missing YouTube API key")

        return build("youtube", "v3", developerKey=settings.youtube_api_key)

    def scrape(self) -> list[dict[str, Any]]:
        """
        Fetch comments from Myntra-related YouTube videos.

        Strategy:
        1. Search for Myntra haul/review videos using multiple queries
        2. For each video, fetch comment threads
        3. Each comment becomes a separate record with video context
        """
        try:
            youtube = self._get_youtube_client()
        except (ImportError, ValueError) as e:
            self._logger.error("Cannot initialize YouTube client: %s", e)
            return []

        # Step 1: Find relevant videos
        video_ids = self._search_videos(youtube)
        self._logger.info("Found %d unique Myntra-related videos", len(video_ids))

        # Step 2: Fetch comments from each video
        all_comments: list[dict[str, Any]] = []

        for video_id, video_title in video_ids.items():
            if len(all_comments) >= self.max_records:
                break

            try:
                comments = self._fetch_video_comments(youtube, video_id, video_title)
                all_comments.extend(comments)
                self._logger.info(
                    "Fetched %d comments from video '%s' (total: %d)",
                    len(comments),
                    video_title[:50],
                    len(all_comments),
                )
            except Exception as e:
                self._logger.warning(
                    "Failed to fetch comments for video %s: %s",
                    video_id,
                    e,
                )

            self._rate_limit()

        self._logger.info("Total YouTube comments fetched: %d", len(all_comments))
        return all_comments[: self.max_records]

    def _search_videos(self, youtube: Any) -> dict[str, str]:
        """
        Search for Myntra-related videos across multiple queries.

        Returns:
            Dict mapping video_id → video_title.
        """
        video_map: dict[str, str] = {}

        for query in self.search_queries:
            if len(video_map) >= self.max_videos:
                break

            try:
                request = youtube.search().list(
                    q=query,
                    part="id,snippet",
                    maxResults=min(10, self.max_videos - len(video_map)),
                    type="video",
                    relevanceLanguage="en",
                    order="relevance",
                )
                response = self._retry_with_backoff(request.execute)

                for item in response.get("items", []):
                    vid_id = item["id"]["videoId"]
                    vid_title = item["snippet"]["title"]
                    if vid_id not in video_map:
                        video_map[vid_id] = vid_title

                self._rate_limit()

            except Exception as e:
                self._logger.warning(
                    "Video search failed for query '%s': %s",
                    query,
                    e,
                )

        return video_map

    def _fetch_video_comments(
        self,
        youtube: Any,
        video_id: str,
        video_title: str,
    ) -> list[dict[str, Any]]:
        """
        Fetch comment threads for a specific video.

        Returns list of raw comment dicts with video context attached.
        """
        comments: list[dict[str, Any]] = []
        next_page_token = None

        while len(comments) < self.max_comments_per_video:
            try:
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=min(100, self.max_comments_per_video - len(comments)),
                    order="relevance",
                    pageToken=next_page_token,
                )
                response = self._retry_with_backoff(request.execute)

                for item in response.get("items", []):
                    snippet = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "comment_id": item["id"],
                        "video_id": video_id,
                        "video_title": video_title,
                        "author": snippet.get("authorDisplayName", ""),
                        "content": snippet.get("textDisplay", ""),
                        "likes": snippet.get("likeCount", 0),
                        "reply_count": item["snippet"].get("totalReplyCount", 0),
                        "published_at": snippet.get("publishedAt", ""),
                    })

                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break

                self._rate_limit()

            except Exception as e:
                self._logger.warning(
                    "Error fetching comments for video %s: %s",
                    video_id,
                    e,
                )
                break

        return comments

    def normalise(self, raw_records: list[dict[str, Any]]) -> list[FeedbackRecord]:
        """Convert YouTube comment dicts to FeedbackRecord instances."""
        records: list[FeedbackRecord] = []

        for raw in raw_records:
            try:
                content = raw.get("content", "")
                if not content or not content.strip():
                    continue

                # Parse timestamp
                published_at = raw.get("published_at", "")
                try:
                    timestamp = datetime.fromisoformat(
                        published_at.replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    timestamp = datetime.now(timezone.utc)

                # Build platform metadata
                metadata = PlatformMetadata(
                    video_title=raw.get("video_title", ""),
                    video_id=raw.get("video_id", ""),
                    likes=raw.get("likes", 0),
                    reply_count=raw.get("reply_count", 0),
                    review_id=raw.get("comment_id", ""),
                    is_comment=True,
                )

                source_url = f"https://www.youtube.com/watch?v={raw.get('video_id', '')}"

                record = FeedbackRecord(
                    source=SourceEnum.YOUTUBE,
                    source_url=source_url,
                    author_id_hash=raw.get("author", "anonymous_youtube"),
                    content_raw=content,
                    timestamp=timestamp,
                    platform_metadata=metadata,
                )
                records.append(record)

            except Exception as e:
                self._logger.warning(
                    "Failed to normalise YouTube comment: %s (id=%s)",
                    e,
                    raw.get("comment_id", "unknown"),
                )

        return records
