"""
Text Preprocessing Pipeline for the RAG Discovery Engine.

Handles text cleaning, PII anonymisation, and language detection.
Designed for Phase 2 data quality gate.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from cleantext import clean
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Seed for deterministic language detection
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

# Regex patterns for PII scrubbing
EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
# Basic phone number pattern (covers Indian formats mostly, e.g. +91 9876543210, 98765-43210)
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[\s-]?)?(\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}")


class TextCleaner:
    """
    Cleans raw text data for NLP processing and RAG indexing.
    """

    def __init__(self) -> None:
        pass

    def clean_text(self, text: str) -> str:
        """
        Full text cleaning pipeline:
        - Strips HTML
        - Normalizes Unicode
        - Standardizes Emojis
        - Removes URLs
        - Standardizes whitespace
        """
        if not text or not isinstance(text, str):
            return ""

        # Remove HTML tags manually using regex since clean-text doesn't do it natively
        text = re.sub(r"<[^>]+>", " ", text)
        
        # Using clean-text library
        cleaned = clean(
            text,
            fix_unicode=True,               # fix various unicode errors
            to_ascii=False,                 # keep unicode (e.g. emojis/accents)
            lower=False,                    # preserve case for Named Entities
            no_line_breaks=True,            # fully strip line breaks
            no_urls=True,                   # replace all URLs with <URL> (we will remove them)
            replace_with_url="",            # Replace URLs with nothing
            no_emails=False,                # we handle emails with regex
            no_phone_numbers=False,         # we handle phones with regex
            no_numbers=False,
            no_digits=False,
            no_currency_symbols=False,
            no_punct=False,                 # keep punctuation for sentiment
        )
        
        # Remove extra whitespace left by URL replacement
        return re.sub(r"\s+", " ", cleaned).strip()

    def scrub_pii(self, text: str) -> str:
        """
        Redact Personally Identifiable Information (PII) like Emails and Phone Numbers.
        """
        text = EMAIL_REGEX.sub("[EMAIL]", text)
        text = PHONE_REGEX.sub("[PHONE]", text)
        return text

    def detect_language(self, text: str) -> str:
        """
        Detects the primary language of the text.
        Returns 'unknown' if detection fails.
        """
        try:
            # langdetect works best with at least a few words
            if len(text.split()) < 3:
                return "unknown"
            return detect(text)
        except LangDetectException:
            return "unknown"

    def process_record(self, raw_text: str) -> dict[str, Any]:
        """
        Run the full cleaning pipeline on a raw text string.
        Returns a dictionary with the cleaned text and metadata.
        """
        scrubbed = self.scrub_pii(raw_text)
        cleaned = self.clean_text(scrubbed)
        lang = self.detect_language(cleaned)

        return {
            "content_cleaned": cleaned,
            "language": lang,
            "is_supported_language": lang in ["en", "unknown"]  # Allow english or short/unknown text
        }

