"""
Reddit Scraper for Myntra-related Posts and Comments.

Fetches posts and comments from Myntra-related subreddits using
PRAW (Python Reddit API Wrapper). Targets ≥ 1,000 authentic
posts+comments.

Features:
  - Targets r/IndianFashionAddicts, r/TwoXIndia, r/myntra
  - Fetches both posts and all comment trees
  - Searches for Myntra-related keywords across subreddits
  - Extracts post title, body, comments, upvotes, subreddit context
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

# Target subreddits for Myntra-related content
TARGET_SUBREDDITS = [
    "IndianFashionAddicts",
    "TwoXIndia",
    "myntra",
    "india",
    "IndianSkincareAddicts",  # Occasional fashion discussions
]

# Search keywords for finding Myntra-related posts
SEARCH_KEYWORDS = [
    "myntra",
    "myntra haul",
    "myntra review",
    "myntra return",
    "myntra sale",
    "EORS",
    "myntra wishlist",
    "myntra size",
    "myntra delivery",
]


class RedditScraper(BaseScraper):
    """
    Scraper for Reddit posts and comments mentioning Myntra.

    Uses PRAW (Python Reddit API Wrapper) with OAuth for authenticated
    access. Fetches both top-level posts and their comment trees from
    targeted subreddits.
    """

    SOURCE_NAME = "reddit"

    def __init__(
        self,
        max_records: int | None = None,
        subreddits: list[str] | None = None,
        search_keywords: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(max_records=max_records or 1000, rate_limit_delay=2.0, **kwargs)
        self.subreddits = subreddits or TARGET_SUBREDDITS
        self.search_keywords = search_keywords or SEARCH_KEYWORDS

    def _get_reddit_client(self) -> Any:
        """Create and return a PRAW Reddit client."""
        try:
            import praw
        except ImportError:
            self._logger.error("praw not installed. Run: pip install praw")
            raise

        settings = get_settings()

        if not settings.reddit_client_id or not settings.reddit_client_secret:
            self._logger.error(
                "Reddit API credentials not configured. "
                "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env"
            )
            raise ValueError("Missing Reddit API credentials")

        return praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )

    def scrape(self) -> list[dict[str, Any]]:
        """
        Fetch Myntra-related posts and comments from Reddit.

        Strategy:
        1. Search each target subreddit for Myntra keywords
        2. Fetch all comments on matching posts
        3. Each post and each comment becomes a separate record
        """
        try:
            reddit = self._get_reddit_client()
        except (ImportError, ValueError) as e:
            self._logger.error("Cannot initialize Reddit client: %s", e)
            return []

        all_records: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        for subreddit_name in self.subreddits:
            if len(all_records) >= self.max_records:
                break

            self._logger.info(
                "Searching r/%s for Myntra-related content",
                subreddit_name,
            )

            try:
                subreddit = reddit.subreddit(subreddit_name)

                for keyword in self.search_keywords:
                    if len(all_records) >= self.max_records:
                        break

                    try:
                        search_results = subreddit.search(
                            keyword,
                            sort="relevance",
                            time_filter="all",
                            limit=50,
                        )

                        for submission in search_results:
                            if len(all_records) >= self.max_records:
                                break

                            # Add the post itself
                            if submission.id not in seen_ids:
                                seen_ids.add(submission.id)
                                all_records.append(
                                    self._submission_to_dict(submission, subreddit_name)
                                )

                            # Fetch and add comments
                            try:
                                submission.comments.replace_more(limit=3)
                                for comment in submission.comments.list():
                                    if len(all_records) >= self.max_records:
                                        break
                                    if comment.id not in seen_ids:
                                        seen_ids.add(comment.id)
                                        all_records.append(
                                            self._comment_to_dict(
                                                comment, submission, subreddit_name
                                            )
                                        )
                            except Exception as e:
                                self._logger.warning(
                                    "Error fetching comments for post %s: %s",
                                    submission.id,
                                    e,
                                )

                            self._rate_limit()

                    except Exception as e:
                        self._logger.warning(
                            "Search failed for keyword '%s' in r/%s: %s",
                            keyword,
                            subreddit_name,
                            e,
                        )

            except Exception as e:
                self._logger.warning(
                    "Failed to access subreddit r/%s: %s",
                    subreddit_name,
                    e,
                )

        self._logger.info("Total Reddit records fetched: %d", len(all_records))
        return all_records

    @staticmethod
    def _submission_to_dict(submission: Any, subreddit_name: str) -> dict[str, Any]:
        """Convert a PRAW Submission to a raw record dict."""
        content = submission.title or ""
        if submission.selftext:
            content = f"{content}\n\n{submission.selftext}"

        return {
            "type": "post",
            "id": submission.id,
            "subreddit": subreddit_name,
            "title": submission.title,
            "content": content,
            "author": str(submission.author) if submission.author else "[deleted]",
            "score": submission.score,
            "upvote_ratio": getattr(submission, "upvote_ratio", None),
            "num_comments": submission.num_comments,
            "created_utc": submission.created_utc,
            "url": f"https://reddit.com{submission.permalink}",
            "is_comment": False,
        }

    @staticmethod
    def _comment_to_dict(
        comment: Any,
        submission: Any,
        subreddit_name: str,
    ) -> dict[str, Any]:
        """Convert a PRAW Comment to a raw record dict."""
        return {
            "type": "comment",
            "id": comment.id,
            "subreddit": subreddit_name,
            "title": submission.title,
            "content": comment.body or "",
            "author": str(comment.author) if comment.author else "[deleted]",
            "score": comment.score,
            "created_utc": comment.created_utc,
            "url": f"https://reddit.com{comment.permalink}",
            "parent_id": comment.parent_id,
            "is_comment": True,
        }

    def normalise(self, raw_records: list[dict[str, Any]]) -> list[FeedbackRecord]:
        """Convert Reddit post/comment dicts to FeedbackRecord instances."""
        records: list[FeedbackRecord] = []

        for raw in raw_records:
            try:
                content = raw.get("content", "")
                if not content or not content.strip() or content == "[deleted]" or content == "[removed]":
                    continue

                # Parse timestamp
                created_utc = raw.get("created_utc", 0)
                timestamp = datetime.fromtimestamp(created_utc, tz=timezone.utc)

                # Build platform metadata
                metadata = PlatformMetadata(
                    subreddit=raw.get("subreddit", ""),
                    score=raw.get("score", 0),
                    upvotes=raw.get("score", 0),  # Reddit score ≈ net upvotes
                    reply_count=raw.get("num_comments"),
                    review_id=raw.get("id", ""),
                    parent_id=raw.get("parent_id"),
                    is_comment=raw.get("is_comment", False),
                )

                record = FeedbackRecord(
                    source=SourceEnum.REDDIT,
                    source_url=raw.get("url", ""),
                    author_id_hash=raw.get("author", "anonymous_reddit"),
                    content_raw=content,
                    timestamp=timestamp,
                    platform_metadata=metadata,
                )
                records.append(record)

            except Exception as e:
                self._logger.warning(
                    "Failed to normalise Reddit record: %s (id=%s)",
                    e,
                    raw.get("id", "unknown"),
                )

        return records
