"""
Twitter/X Scraper for Myntra-related Tweets.

Fetches tweets and replies mentioning Myntra using the X API v2
via tweepy. Targets ≥ 500 authentic tweets.

Features:
  - Multiple search queries: "myntra", #myntra, @myntra
  - Fetches tweets + engagement metrics
  - Extracts tweet text, likes, retweets, hashtags, mentions
  - Handles API v2 pagination
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

# Search queries for Myntra-related tweets
TWITTER_SEARCH_QUERIES = [
    "myntra -is:retweet lang:en",
    "#myntra -is:retweet lang:en",
    "@mynaborig -is:retweet lang:en",
    "myntra haul -is:retweet lang:en",
    "myntra review -is:retweet lang:en",
    "myntra return -is:retweet lang:en",
    "myntra sale -is:retweet lang:en",
    "myntra delivery -is:retweet lang:en",
]


class TwitterScraper(BaseScraper):
    """
    Scraper for tweets mentioning Myntra on X (Twitter).

    Uses tweepy with X API v2 Bearer Token authentication.
    Fetches recent tweets matching Myntra-related search queries.
    """

    SOURCE_NAME = "twitter"

    def __init__(
        self,
        max_records: int | None = None,
        search_queries: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(max_records=max_records or 500, rate_limit_delay=2.0, **kwargs)
        self.search_queries = search_queries or TWITTER_SEARCH_QUERIES

    def _get_twitter_client(self) -> Any:
        """Create and return a tweepy Client for API v2."""
        try:
            import tweepy
        except ImportError:
            self._logger.error(
                "tweepy not installed. Run: pip install tweepy"
            )
            raise

        settings = get_settings()

        if not settings.twitter_bearer_token:
            self._logger.error(
                "Twitter Bearer Token not configured. "
                "Set TWITTER_BEARER_TOKEN in .env"
            )
            raise ValueError("Missing Twitter Bearer Token")

        return tweepy.Client(
            bearer_token=settings.twitter_bearer_token,
            wait_on_rate_limit=True,
        )

    def scrape(self) -> list[dict[str, Any]]:
        """
        Fetch Myntra-related tweets from X (Twitter).

        Uses the recent search endpoint (last 7 days) with multiple
        queries to maximize coverage.
        """
        try:
            client = self._get_twitter_client()
        except (ImportError, ValueError) as e:
            self._logger.error("Cannot initialize Twitter client: %s", e)
            return []

        all_tweets: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        for query in self.search_queries:
            if len(all_tweets) >= self.max_records:
                break

            remaining = min(100, self.max_records - len(all_tweets))
            self._logger.info(
                "Searching Twitter for: '%s' (max %d)",
                query,
                remaining,
            )

            try:
                # Use paginator for automatic pagination
                import tweepy

                paginator = tweepy.Paginator(
                    client.search_recent_tweets,
                    query=query,
                    max_results=min(100, remaining),
                    tweet_fields=["created_at", "public_metrics", "entities", "author_id", "conversation_id"],
                    expansions=["author_id"],
                    user_fields=["username"],
                )

                for response in paginator:
                    if len(all_tweets) >= self.max_records:
                        break

                    if not response.data:
                        break

                    # Build author lookup from includes
                    author_map: dict[str, str] = {}
                    if response.includes and "users" in response.includes:
                        for user in response.includes["users"]:
                            author_map[user.id] = user.username

                    for tweet in response.data:
                        if str(tweet.id) not in seen_ids:
                            seen_ids.add(str(tweet.id))

                            # Extract hashtags
                            hashtags: list[str] = []
                            if tweet.entities and "hashtags" in tweet.entities:
                                hashtags = [h["tag"] for h in tweet.entities["hashtags"]]

                            metrics = tweet.public_metrics or {}

                            all_tweets.append({
                                "id": str(tweet.id),
                                "text": tweet.text,
                                "author_id": str(tweet.author_id),
                                "author_username": author_map.get(tweet.author_id, ""),
                                "created_at": tweet.created_at.isoformat() if tweet.created_at else "",
                                "likes": metrics.get("like_count", 0),
                                "retweet_count": metrics.get("retweet_count", 0),
                                "reply_count": metrics.get("reply_count", 0),
                                "hashtags": hashtags,
                                "conversation_id": str(tweet.conversation_id) if tweet.conversation_id else "",
                            })

                    self._rate_limit()

            except Exception as e:
                self._logger.warning(
                    "Twitter search failed for query '%s': %s",
                    query,
                    e,
                )

        self._logger.info("Total tweets fetched: %d", len(all_tweets))
        return all_tweets[: self.max_records]

    def normalise(self, raw_records: list[dict[str, Any]]) -> list[FeedbackRecord]:
        """Convert Twitter tweet dicts to FeedbackRecord instances."""
        records: list[FeedbackRecord] = []

        for raw in raw_records:
            try:
                content = raw.get("text", "")
                if not content or not content.strip():
                    continue

                # Parse timestamp
                created_at = raw.get("created_at", "")
                try:
                    timestamp = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    timestamp = datetime.now(timezone.utc)

                # Build platform metadata
                metadata = PlatformMetadata(
                    likes=raw.get("likes", 0),
                    retweet_count=raw.get("retweet_count", 0),
                    reply_count=raw.get("reply_count", 0),
                    hashtags=raw.get("hashtags", []),
                    review_id=raw.get("id", ""),
                )

                tweet_id = raw.get("id", "")
                author_username = raw.get("author_username", "")
                source_url = (
                    f"https://x.com/{author_username}/status/{tweet_id}"
                    if author_username
                    else f"https://x.com/i/status/{tweet_id}"
                )

                record = FeedbackRecord(
                    source=SourceEnum.TWITTER,
                    source_url=source_url,
                    author_id_hash=raw.get("author_id", "anonymous_twitter"),
                    content_raw=content,
                    timestamp=timestamp,
                    platform_metadata=metadata,
                )
                records.append(record)

            except Exception as e:
                self._logger.warning(
                    "Failed to normalise tweet: %s (id=%s)",
                    e,
                    raw.get("id", "unknown"),
                )

        return records
