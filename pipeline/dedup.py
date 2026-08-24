"""
Deduplication Engine for the RAG Discovery Engine.

Implements:
1. Exact Deduplication (using SHA-256 fingerprint)
2. Near Deduplication (using MinHash LSH)
"""

from __future__ import annotations

import logging
from typing import Any

from datasketch import MinHash, MinHashLSH

logger = logging.getLogger(__name__)


class DedupEngine:
    """
    Deduplication engine using MinHash LSH for near-duplicate detection.
    """

    def __init__(self, threshold: float = 0.85, num_perm: int = 128) -> None:
        """
        Initialize the Deduplication engine.
        
        Args:
            threshold: Jaccard similarity threshold (0.0 to 1.0)
            num_perm: Number of permutations for MinHash (higher = more accurate but slower)
        """
        self.threshold = threshold
        self.num_perm = num_perm
        self.lsh = MinHashLSH(threshold=self.threshold, num_perm=self.num_perm)
        self.seen_fingerprints: set[str] = set()

    def _get_minhash(self, text: str) -> MinHash:
        """Compute the MinHash signature for a given text using character tri-grams."""
        m = MinHash(num_perm=self.num_perm)
        text = text.lower()
        if len(text) < 3:
            m.update(text.encode("utf8"))
            return m
            
        # Character tri-grams
        for i in range(len(text) - 2):
            shingle = text[i:i+3]
            m.update(shingle.encode("utf8"))
        return m

    def is_duplicate(self, record_id: str, text: str, fingerprint: str) -> bool:
        """
        Check if a record is a duplicate (exact or near).
        If not a duplicate, it gets added to the LSH index.
        
        Args:
            record_id: Unique identifier for the record.
            text: Cleaned text to check for near-duplicates.
            fingerprint: SHA-256 fingerprint for exact-duplicates.
            
        Returns:
            True if it's a duplicate, False otherwise.
        """
        # 1. Exact Duplicate Check
        if fingerprint in self.seen_fingerprints:
            return True

        # 2. Near Duplicate Check
        m = self._get_minhash(text)
        result = self.lsh.query(m)
        
        if result:
            # Near duplicate found
            return True
            
        # Not a duplicate -> insert into index
        self.seen_fingerprints.add(fingerprint)
        self.lsh.insert(record_id, m)
        return False

    def clear(self) -> None:
        """Clear the in-memory LSH index and seen fingerprints."""
        self.lsh = MinHashLSH(threshold=self.threshold, num_perm=self.num_perm)
        self.seen_fingerprints.clear()
