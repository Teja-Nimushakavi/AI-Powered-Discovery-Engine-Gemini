"""
Centralised application settings loaded from environment variables.

Uses Pydantic Settings to validate and type-check all configuration
at startup. Missing critical variables will raise immediately.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Resolve project root (two levels up from config/settings.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings — loaded from .env file and environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Reddit API (PRAW) ──────────────────────────────────────────────
    reddit_client_id: str = Field(default="", description="Reddit OAuth app client ID")
    reddit_client_secret: str = Field(default="", description="Reddit OAuth app client secret")
    reddit_user_agent: str = Field(
        default="MyntraRAG/0.1",
        description="User-Agent string for Reddit API",
    )

    # ── YouTube Data API v3 ────────────────────────────────────────────
    youtube_api_key: str = Field(default="", description="YouTube Data API v3 key")

    # ── X (Twitter) API v2 ─────────────────────────────────────────────
    twitter_bearer_token: str = Field(default="", description="Twitter/X API v2 bearer token")

    # ── Instagram ──────────────────────────────────────────────────────
    instagram_access_token: str = Field(default="", description="Instagram Graph API access token")
    instagram_business_account_id: str = Field(default="", description="Instagram Business Account ID")
    instagram_use_instaloader: bool = Field(
        default=True,
        description="Use Instaloader (public scraping) instead of Graph API",
    )

    # ── LLM & APIs ─────────────────────────────────────────────────────
    google_api_key: str | None = Field(default=None)

    # ── Database (Phase 2) ─────────────────────────────────────────────
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="myntra_rag")
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")

    # ── ChromaDB (Phase 3) ─────────────────────────────────────────────
    chromadb_host: str = Field(default="localhost")
    chromadb_port: int = Field(default=8000)

    # ── Redis (Phase 2) ────────────────────────────────────────────────
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)

    # ── Scraper Defaults ───────────────────────────────────────────────
    default_max_records: int = Field(default=500, description="Default max records per scraper run")
    raw_data_dir: str = Field(default="data/raw", description="Output dir for raw JSONL files")
    log_level: str = Field(default="INFO", description="Logging level")

    # ── Derived Properties ─────────────────────────────────────────────

    @property
    def raw_data_path(self) -> Path:
        """Resolved absolute path to the raw data staging directory."""
        path = PROJECT_ROOT / self.raw_data_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def postgres_url(self) -> str:
        """SQLAlchemy-compatible SQLite connection URL (changed from Postgres for local dev)."""
        db_path = PROJECT_ROOT / "myntra_rag.db"
        return f"sqlite:///{db_path}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get cached application settings singleton.
    
    Settings are loaded once and cached for the lifetime of the process.
    """
    return Settings()
