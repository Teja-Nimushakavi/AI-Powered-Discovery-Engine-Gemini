"""
Synthetic Data Filter for the RAG Discovery Engine.

Implements:
1. Bot filtering heuristics
2. LLM-generated text detection (stub for Phase 2)
"""

from __future__ import annotations

import logging
import re
from typing import Any, Tuple

logger = logging.getLogger(__name__)


class SyntheticFilter:
    """
    Filters out bot-generated and synthetic (LLM-generated) content.
    """

    def __init__(self) -> None:
        # Simple heuristic patterns to catch obvious bots
        self.bot_patterns = [
            re.compile(r"click here to earn", re.IGNORECASE),
            re.compile(r"link in bio.*discount", re.IGNORECASE),
            re.compile(r"https?://\S+"),  # Heavy URL presence is suspicious if not caught by cleaner
            re.compile(r"(?:\b(?:buy|cheap|followers|crypto|bitcoin)\b.*?){3,}", re.IGNORECASE)
        ]

        # Simple heuristic patterns to catch obvious LLM generations (until API integration)
        self.llm_patterns = [
            re.compile(r"as an ai language model", re.IGNORECASE),
            re.compile(r"i cannot fulfill this request", re.IGNORECASE),
            re.compile(r"it is important to note that", re.IGNORECASE),
            re.compile(r"in conclusion,", re.IGNORECASE),
            re.compile(r"this review highlights the importance of", re.IGNORECASE)
        ]

    def _is_bot(self, text: str) -> bool:
        """Check text against known bot heuristic patterns."""
        for pattern in self.bot_patterns:
            if pattern.search(text):
                return True
                
        # Frequency check (too many identical characters)
        if len(text) > 20 and len(set(text)) < 5:
            return True
            
        return False

    def _is_synthetic(self, text: str) -> bool:
        """
        Check if text is LLM generated.
        Currently uses simple regex stubs. 
        In production, this would call GPTZero or Binoculars API.
        """
        for pattern in self.llm_patterns:
            if pattern.search(text):
                return True
        return False

    def evaluate(self, text: str) -> Tuple[bool, str, float]:
        """
        Evaluate a piece of text.
        
        Returns:
            Tuple of (is_flagged, flag_reason, flag_score)
        """
        if not text or len(text.strip()) < 5:
            return True, "TOO_SHORT", 1.0

        if self._is_bot(text):
            return True, "BOT_HEURISTIC", 0.9

        if self._is_synthetic(text):
            return True, "SYNTHETIC_LLM", 0.8

        return False, "", 0.0
