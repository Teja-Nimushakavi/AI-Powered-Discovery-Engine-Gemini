"""
Tests for the Text Cleaner module.
"""

from __future__ import annotations

from nlp.cleaner import TextCleaner


def test_clean_text_basic():
    cleaner = TextCleaner()
    # Test HTML stripping and unicode fixing
    text = "<p>This is a <b>test</b> of the â€œsmart quotesâ€\x9d.</p>"
    cleaned = cleaner.clean_text(text)
    assert 'This is a test of the "smart quotes".' in cleaned


def test_clean_text_removes_urls():
    cleaner = TextCleaner()
    text = "Check out this link https://myntra.com/sale and this one http://google.com!"
    cleaned = cleaner.clean_text(text)
    assert "Check out this link and this one !" in cleaned
    assert "http" not in cleaned


def test_scrub_pii():
    cleaner = TextCleaner()
    text = "Contact me at user.name@email.com or call +91 9876543210 for details."
    scrubbed = cleaner.scrub_pii(text)
    assert "[EMAIL]" in scrubbed
    assert "user.name@email.com" not in scrubbed
    assert "[PHONE]" in scrubbed
    assert "9876543210" not in scrubbed


def test_detect_language():
    cleaner = TextCleaner()
    
    # English
    en_text = "This is a completely normal English sentence."
    assert cleaner.detect_language(en_text) == "en"
    
    # Hindi (Devanagari)
    hi_text = "यह एक बहुत अच्छा उत्पाद है"
    assert cleaner.detect_language(hi_text) != "en"
    
    # Too short
    short_text = "Hi"
    assert cleaner.detect_language(short_text) == "unknown"


def test_process_record():
    cleaner = TextCleaner()
    raw = "My email is test@test.com! Love this <p>app</p> https://link.com"
    result = cleaner.process_record(raw)
    
    cleaned = result["content_cleaned"]
    assert "[EMAIL]" in cleaned
    assert "app" in cleaned
    assert "<p>" not in cleaned
    assert "https://" not in cleaned
    assert result["is_supported_language"] is True
