"""
Tests for the Deduplication Engine.
"""

from __future__ import annotations

from pipeline.dedup import DedupEngine


def test_exact_duplicate():
    engine = DedupEngine()
    
    # First time seeing the fingerprint
    is_dup1 = engine.is_duplicate("rec1", "This is some text", "fingerprint_1")
    assert is_dup1 is False
    
    # Second time seeing the exact fingerprint
    is_dup2 = engine.is_duplicate("rec2", "This is completely different text", "fingerprint_1")
    assert is_dup2 is True


def test_near_duplicate():
    engine = DedupEngine(threshold=0.8)
    
    text1 = "The quick brown fox jumps over the lazy dog and runs away."
    text2 = "The quick brown fox jumps over the lazy dog and walks away."
    
    is_dup1 = engine.is_duplicate("rec1", text1, "fp1")
    assert is_dup1 is False
    
    # Text2 is extremely similar to Text1, should flag as near duplicate
    is_dup2 = engine.is_duplicate("rec2", text2, "fp2")
    assert is_dup2 is True


def test_not_duplicate():
    engine = DedupEngine(threshold=0.8)
    
    text1 = "This dress has a terrible sizing issue, I ordered Medium but it feels like Extra Small."
    text2 = "The delivery was delayed by three days, very unhappy with the logistics."
    
    is_dup1 = engine.is_duplicate("rec1", text1, "fp1")
    assert is_dup1 is False
    
    is_dup2 = engine.is_duplicate("rec2", text2, "fp2")
    assert is_dup2 is False
