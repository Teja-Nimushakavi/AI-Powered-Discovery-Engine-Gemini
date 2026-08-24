"""
Shared test fixtures for the RAG Discovery Engine test suite.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

# Set empty API keys for testing
os.environ.setdefault("REDDIT_CLIENT_ID", "test_client_id")
os.environ.setdefault("REDDIT_CLIENT_SECRET", "test_client_secret")
os.environ.setdefault("YOUTUBE_API_KEY", "test_youtube_key")
os.environ.setdefault("TWITTER_BEARER_TOKEN", "test_twitter_token")
os.environ.setdefault("INSTAGRAM_ACCESS_TOKEN", "")
os.environ.setdefault("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for scraper JSONL output."""
    output_dir = tmp_path / "data" / "raw"
    output_dir.mkdir(parents=True)
    return output_dir


@pytest.fixture
def sample_playstore_reviews() -> list[dict[str, Any]]:
    """Sample raw Play Store review data."""
    return [
        {
            "reviewId": "gp_review_001",
            "userName": "TestUser1",
            "content": "The app is great but sizing is always off. Ordered M but it fits like an S. Myntra needs better size charts.",
            "score": 3,
            "thumbsUpCount": 15,
            "reviewCreatedVersion": "4.2.1",
            "at": datetime(2024, 6, 15, 10, 30, 0),
        },
        {
            "reviewId": "gp_review_002",
            "userName": "TestUser2",
            "content": "Love the EORS sale! Got amazing deals on ethnic wear. Wishlist feature helped me track price drops.",
            "score": 5,
            "thumbsUpCount": 42,
            "reviewCreatedVersion": "4.2.3",
            "at": datetime(2024, 7, 1, 14, 0, 0),
        },
        {
            "reviewId": "gp_review_003",
            "userName": "TestUser3",
            "content": "Return policy is terrible now. They charge convenience fee for returns. Won't buy anymore.",
            "score": 1,
            "thumbsUpCount": 89,
            "reviewCreatedVersion": "4.2.3",
            "at": datetime(2024, 7, 10, 8, 0, 0),
        },
        {
            "reviewId": "gp_review_004",
            "userName": "TestUser4",
            "content": "",  # Empty review — should be skipped
            "score": 4,
            "thumbsUpCount": 0,
            "at": datetime(2024, 7, 12, 12, 0, 0),
        },
    ]


@pytest.fixture
def sample_appstore_reviews() -> list[dict[str, Any]]:
    """Sample raw App Store review data."""
    return [
        {
            "title": "Good app but needs improvement",
            "review": "Colors shown in app don't match actual product. Fabric looks different in photos vs reality.",
            "rating": 3,
            "date": datetime(2024, 6, 20, 9, 0, 0),
            "userName": "iPhoneUser1",
            "isEdited": False,
            "_country": "in",
        },
        {
            "title": "Best fashion app",
            "review": "Myntra Insider rewards are awesome! Love the cashback on purchases. FWD section has latest trends.",
            "rating": 5,
            "date": datetime(2024, 7, 5, 16, 0, 0),
            "userName": "iPhoneUser2",
            "isEdited": False,
            "_country": "in",
        },
    ]


@pytest.fixture
def sample_reddit_posts() -> list[dict[str, Any]]:
    """Sample raw Reddit post/comment data."""
    return [
        {
            "type": "post",
            "id": "reddit_001",
            "subreddit": "IndianFashionAddicts",
            "title": "Myntra vs Ajio — which has better return policy?",
            "content": "Myntra vs Ajio — which has better return policy?\n\nI've been shopping on both and Myntra's new return fee is making me reconsider. Ajio has free returns still.",
            "author": "fashionista_23",
            "score": 45,
            "num_comments": 23,
            "created_utc": 1718000000.0,
            "url": "https://reddit.com/r/IndianFashionAddicts/comments/abc123",
            "is_comment": False,
        },
        {
            "type": "comment",
            "id": "reddit_002",
            "subreddit": "IndianFashionAddicts",
            "title": "Myntra vs Ajio — which has better return policy?",
            "content": "I always check YouTube reviews before buying from Myntra. The photos on the app are misleading with studio lighting.",
            "author": "smartshopper_99",
            "score": 12,
            "created_utc": 1718050000.0,
            "url": "https://reddit.com/r/IndianFashionAddicts/comments/abc123/def456",
            "parent_id": "t3_abc123",
            "is_comment": True,
        },
        {
            "type": "comment",
            "id": "reddit_003",
            "subreddit": "myntra",
            "title": "Wishlist items never go on sale",
            "content": "[deleted]",  # Deleted comment — should be skipped
            "author": "[deleted]",
            "score": 0,
            "created_utc": 1718100000.0,
            "url": "https://reddit.com/r/myntra/comments/xyz789",
            "is_comment": True,
        },
    ]


@pytest.fixture
def sample_youtube_comments() -> list[dict[str, Any]]:
    """Sample raw YouTube comment data."""
    return [
        {
            "comment_id": "yt_001",
            "video_id": "abc123xyz",
            "video_title": "HUGE Myntra Haul 2024 | Try On | Worth it?",
            "author": "FashionLover",
            "content": "The Roadster tshirt quality has gone down so much! I compared with HRX and HRX is way better now.",
            "likes": 34,
            "reply_count": 5,
            "published_at": "2024-06-15T12:00:00Z",
        },
        {
            "comment_id": "yt_002",
            "video_id": "abc123xyz",
            "video_title": "HUGE Myntra Haul 2024 | Try On | Worth it?",
            "author": "BudgetShopper",
            "content": "I add everything to wishlist during non-sale period and only buy during EORS. Saves so much money!",
            "likes": 78,
            "reply_count": 12,
            "published_at": "2024-06-16T08:30:00Z",
        },
    ]


@pytest.fixture
def sample_twitter_tweets() -> list[dict[str, Any]]:
    """Sample raw Twitter tweet data."""
    return [
        {
            "id": "tw_001",
            "text": "Just received my @myntra order and the color is completely different from what was shown! 😡 #myntra #colormismatch",
            "author_id": "user_12345",
            "author_username": "angry_customer",
            "created_at": "2024-07-01T10:00:00+00:00",
            "likes": 23,
            "retweet_count": 5,
            "reply_count": 8,
            "hashtags": ["myntra", "colormismatch"],
            "conversation_id": "conv_001",
        },
        {
            "id": "tw_002",
            "text": "Myntra EORS sale was amazing! Got 3 kurtas for the price of 1. The wishlist notification for price drops is a game changer 🎉 #myntra #EORS",
            "author_id": "user_67890",
            "author_username": "happy_shopper",
            "created_at": "2024-07-02T14:30:00+00:00",
            "likes": 56,
            "retweet_count": 12,
            "reply_count": 3,
            "hashtags": ["myntra", "EORS"],
            "conversation_id": "conv_002",
        },
    ]


@pytest.fixture
def sample_instagram_posts() -> list[dict[str, Any]]:
    """Sample raw Instagram post/comment data."""
    return [
        {
            "type": "post",
            "shortcode": "ig_001",
            "caption": "My Myntra haul is here! 🛍️ Love the ethnic collection but the size chart is so confusing. Ordered L but should have gone for XL. #myntra #myntrahaul",
            "author": "fashionista_ig",
            "likes": 234,
            "comments_count": 15,
            "timestamp": "2024-06-25T10:00:00+00:00",
            "hashtags": ["myntra", "myntrahaul"],
            "url": "https://www.instagram.com/p/ig_001/",
            "is_comment": False,
        },
        {
            "type": "comment",
            "shortcode": "ig_002",
            "caption": "Same! The Anouk kurta I ordered looked nothing like the photos. Fabric was see-through 😤",
            "author": "comment_user",
            "likes": 12,
            "timestamp": "2024-06-25T11:30:00+00:00",
            "url": "https://www.instagram.com/p/ig_001/",
            "parent_id": "ig_001",
            "is_comment": True,
        },
    ]
