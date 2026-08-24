"""
Abstract Base Scraper for the RAG Discovery Engine.

All source-specific scrapers inherit from BaseScraper and implement:
  - scrape()      → fetch raw records from the source API
  - normalise()   → convert raw records to unified FeedbackRecord schema

The base class provides:
  - Rate limiting with configurable delays
  - Exponential backoff retry logic
  - JSONL file output with timestamped filenames
  - Logging infrastructure
  - Error handling and partial-result recovery
"""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from models.schema import FeedbackRecord
from config.settings import get_settings


logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for all data source scrapers.

    Provides common infrastructure for rate limiting, retries,
    normalisation, and JSONL output. Each subclass must implement
    `scrape()` and `normalise()`.
    """

    # Subclasses should override this with their source name
    SOURCE_NAME: str = "base"

    def __init__(
        self,
        max_records: int | None = None,
        rate_limit_delay: float = 1.0,
        max_retries: int = 3,
        output_dir: str | Path | None = None,
    ) -> None:
        """
        Initialise the scraper.

        Args:
            max_records: Maximum number of records to fetch. Defaults to
                         settings.default_max_records.
            rate_limit_delay: Seconds to wait between API calls.
            max_retries: Maximum retry attempts on transient failures.
            output_dir: Directory for JSONL output. Defaults to
                        settings.raw_data_path.
        """
        settings = get_settings()
        self.max_records = max_records or settings.default_max_records
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.output_dir = Path(output_dir) if output_dir else settings.raw_data_path
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._logger = logging.getLogger(f"scrapers.{self.SOURCE_NAME}")

    @abstractmethod
    def scrape(self) -> list[dict[str, Any]]:
        """
        Fetch raw records from the source API.

        Returns:
            List of raw record dicts in source-native format.
            Each dict will be passed to normalise() for schema mapping.
        """
        ...

    @abstractmethod
    def normalise(self, raw_records: list[dict[str, Any]]) -> list[FeedbackRecord]:
        """
        Convert raw source records to unified FeedbackRecord schema.

        Args:
            raw_records: List of raw dicts from scrape().

        Returns:
            List of validated FeedbackRecord instances.
        """
        ...

    def run(self) -> list[FeedbackRecord]:
        """
        Execute the full scrape → normalise → save pipeline.

        Returns:
            List of normalised FeedbackRecord instances.
        """
        self._logger.info(
            "Starting %s scraper (max_records=%d)",
            self.SOURCE_NAME,
            self.max_records,
        )

        # Step 1: Scrape raw records
        start_time = time.time()
        raw_records = self.scrape()
        scrape_duration = time.time() - start_time
        self._logger.info(
            "Scraped %d raw records from %s in %.1fs",
            len(raw_records),
            self.SOURCE_NAME,
            scrape_duration,
        )

        if not raw_records:
            self._logger.warning("No records scraped from %s", self.SOURCE_NAME)
            return []

        # Step 2: Normalise to unified schema
        records = self.normalise(raw_records)
        self._logger.info(
            "Normalised %d/%d records (%.1f%% success rate)",
            len(records),
            len(raw_records),
            (len(records) / len(raw_records) * 100) if raw_records else 0,
        )

        # Step 3: Save to JSONL
        if records:
            output_path = self.save(records)
            self._logger.info("Saved %d records to %s", len(records), output_path)

        return records

    def save(self, records: list[FeedbackRecord], filename: str | None = None) -> Path:
        """
        Save normalised records to a JSONL file.

        Args:
            records: List of FeedbackRecord instances to save.
            filename: Optional custom filename. Defaults to
                      {source}_{timestamp}.jsonl

        Returns:
            Path to the created JSONL file.
        """
        if filename is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"{self.SOURCE_NAME}_{timestamp}.jsonl"

        output_path = self.output_dir / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            for record in records:
                json_line = json.dumps(record.to_jsonl_dict(), ensure_ascii=False)
                f.write(json_line + "\n")

        return output_path

    def _rate_limit(self) -> None:
        """Sleep for the configured rate limit delay."""
        if self.rate_limit_delay > 0:
            time.sleep(self.rate_limit_delay)

    def _retry_with_backoff(
        self,
        func: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function with exponential backoff retry logic.

        Args:
            func: The function to call.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            The function's return value on success.

        Raises:
            The last exception if all retries are exhausted.
        """
        last_exception: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                wait_time = (2 ** attempt) + (0.1 * attempt)  # Exponential backoff with jitter
                self._logger.warning(
                    "Attempt %d/%d failed for %s: %s. Retrying in %.1fs...",
                    attempt + 1,
                    self.max_retries,
                    self.SOURCE_NAME,
                    str(e),
                    wait_time,
                )
                time.sleep(wait_time)

        self._logger.error(
            "All %d retries exhausted for %s",
            self.max_retries,
            self.SOURCE_NAME,
        )
        raise last_exception  # type: ignore[misc]
