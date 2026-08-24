"""
Tests for NLP Analyzer.
"""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest
from nlp.analyzer import NLPAnalyzer


@pytest.fixture
def mock_analyzer():
    """Returns an NLPAnalyzer with mocked HuggingFace pipelines."""
    with patch("nlp.analyzer.pipeline") as mock_pipeline:
        # Mock the pipeline factory to return simple mock functions
        
        def mock_pipeline_factory(task, **kwargs):
            if task == "sentiment-analysis":
                # Returns a mock callable for sentiment
                def mock_sentiment(text):
                    if "love" in text.lower():
                        return [{"label": "positive", "score": 0.99}]
                    elif "hate" in text.lower() or "terrible" in text.lower():
                        return [{"label": "negative", "score": 0.95}]
                    else:
                        return [{"label": "neutral", "score": 0.8}]
                return mock_sentiment
                
            elif task == "zero-shot-classification":
                # Returns a mock callable for zero-shot
                def mock_zero_shot(text, candidate_labels, **kwargs_inner):
                    if "size" in text.lower() or "fit" in text.lower():
                        return {"labels": ["Size/Fit", "Product comparison"], "scores": [0.85, 0.1]}
                    elif "price" in text.lower():
                        return {"labels": ["Price", "Discount waiting"], "scores": [0.9, 0.05]}
                    else:
                        return {"labels": ["Direct"], "scores": [0.9]}
                return mock_zero_shot
                
        mock_pipeline.side_effect = mock_pipeline_factory
        
        analyzer = NLPAnalyzer(device=-1)
        return analyzer


def test_sentiment_analysis(mock_analyzer):
    pos_result = mock_analyzer.analyze_sentiment("I absolutely love this dress!")
    assert pos_result["label"] == "positive"
    assert pos_result["score"] == 0.99
    
    neg_result = mock_analyzer.analyze_sentiment("The fabric is terrible and itchy.")
    assert neg_result["label"] == "negative"
    
    neu_result = mock_analyzer.analyze_sentiment("It is a shirt.")
    assert neu_result["label"] == "neutral"


def test_label_classification(mock_analyzer):
    # Text mentioning fit should trigger the Size/Fit label above 0.3 threshold
    barriers = mock_analyzer.classify_labels("The size was way too small", labels=["Size/Fit", "Product comparison"], threshold=0.3)
    labels = [b["label"] for b in barriers]
    assert "Size/Fit" in labels
    assert "Product comparison" not in labels # score is 0.1, threshold 0.3
    
    # Empty text
    assert mock_analyzer.classify_labels("", labels=[]) == []


def test_segment_tagging(mock_analyzer):
    # Gen Z keyword
    text1 = "This oversized hoodie has such a good vibe."
    segments1 = mock_analyzer.tag_segments(text1)
    assert "Gen Z" in segments1
    
    # Price sensitive keyword
    text2 = "Waiting for the price drop during EORS."
    segments2 = mock_analyzer.tag_segments(text2)
    assert "Price-Sensitive" in segments2
    
    # Multiple segments
    text3 = "I bought this expensive designer dress for a wedding vibe."
    segments3 = mock_analyzer.tag_segments(text3)
    assert "Premium Buyer" in segments3
    assert "Gen Z" in segments3 # "vibe"


def test_enrich_record(mock_analyzer):
    text = "I love this oversized shirt but the size is weird."
    result = mock_analyzer.enrich_record(text)
    
    assert "sentiment" in result
    assert result["sentiment"]["label"] == "positive"
    
    assert "purchase_barriers" in result
    barrier_labels = [b["label"] for b in result["purchase_barriers"]]
    assert "Size/Fit" in barrier_labels
    
    assert "segments" in result
    assert "Gen Z" in result["segments"]
