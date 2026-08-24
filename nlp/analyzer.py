"""
NLP Analyzer for the RAG Discovery Engine.

Enriches text with:
1. Sentiment Analysis (Positive, Neutral, Negative)
2. Zero-Shot Friction Classification
3. User Segment Tagging (Heuristic)
"""

from __future__ import annotations

import logging
from typing import Any

import torch
from transformers import pipeline

logger = logging.getLogger(__name__)

# Wishlist Purchase Barriers
PURCHASE_BARRIERS = [
    "Price",
    "Discount waiting",
    "Size/Fit",
    "Quality uncertainty",
    "Product appearance",
    "Reviews/ratings",
    "Trust",
    "Choice overload",
    "Product comparison",
    "Product discovery",
    "Availability",
    "Delivery",
    "Return/Exchange",
    "Recommendations"
]

# User Behaviours
USER_BEHAVIOURS = [
    "Wishlisted/Saved",
    "Considered but didn't buy",
    "Compared products",
    "Waiting",
    "Purchased"
]

# Relevance Labels
RELEVANCE_LABELS = [
    "Direct",
    "Indirect",
    "Not Relevant"
]

# User Segment Heuristics
USER_SEGMENTS = {
    "Gen Z": ["aesthetic", "vibe", "slay", "drip", "streetwear", "oversized", "sneakers"],
    "Price-Sensitive": ["sale", "discount", "coupon", "expensive", "wait for price drop", "eors"],
    "Premium Buyer": ["wedding", "festive", "designer", "luxury", "expensive"],
    "Myntra Insider": ["insider", "points", "loyal", "elite", "icon"],
}


class NLPAnalyzer:
    """
    Wraps HuggingFace pipelines for NLP enrichment.
    """

    def __init__(self, device: int = -1) -> None:
        """
        Initialize NLP models.
        Args:
            device: -1 for CPU, 0 for GPU.
        """
        logger.info("Loading NLP models (this may take a moment)...")
        
        # Use a fast default sentiment model if cardiffnlp is too heavy for local CPU
        # 'distilbert-base-uncased-finetuned-sst-2-english' is much faster but only Pos/Neg.
        # We stick to cardiffnlp to get Neutral class as per standard.
        self.sentiment_pipe = pipeline(
            "sentiment-analysis", 
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            device=device,
            truncation=True,
            max_length=512
        )
        
        # Zero-shot classification
        self.zero_shot_pipe = pipeline(
            "zero-shot-classification", 
            model="valhalla/distilbart-mnli-12-3", # Lighter version of bart-large-mnli
            device=device
        )
        
        logger.info("NLP models loaded successfully.")

    def analyze_sentiment(self, text: str) -> dict[str, Any]:
        """
        Analyze sentiment of the text.
        Returns mapped scores for positive, neutral, and negative.
        """
        if not text:
            return {"label": "neutral", "score": 1.0}
            
        try:
            # The cardiffnlp model returns labels like 'positive', 'neutral', 'negative'
            result = self.sentiment_pipe(text)[0] # type: ignore
            return {
                "label": result["label"],
                "score": round(result["score"], 4)
            }
        except Exception as e:
            logger.error("Sentiment analysis failed: %s", e)
            return {"label": "neutral", "score": 1.0}

    def classify_labels(self, text: str, labels: list[str], multi_label: bool = True, threshold: float = 0.3) -> list[dict[str, Any]]:
        """
        Classifies the text against predefined labels.
        Returns labels that score above the threshold, or the top label if multi_label is False.
        """
        if not text:
            return []
            
        try:
            result = self.zero_shot_pipe(text, labels, multi_label=multi_label) # type: ignore
            
            classified = []
            if multi_label:
                for label, score in zip(result["labels"], result["scores"]):
                    if score >= threshold:
                        classified.append({"label": label, "score": round(score, 4)})
            else:
                # Just return the top 1
                classified.append({"label": result["labels"][0], "score": round(result["scores"][0], 4)})
                    
            return classified
        except Exception as e:
            logger.error("Zero-shot classification failed: %s", e)
            return []

    def tag_segments(self, text: str) -> list[str]:
        """
        Tag user segments based on heuristic keyword matching.
        """
        text_lower = text.lower()
        segments = []
        
        for segment, keywords in USER_SEGMENTS.items():
            if any(kw in text_lower for kw in keywords):
                segments.append(segment)
                
        return segments

    def enrich_record(self, text: str) -> dict[str, Any]:
        """
        Run the full NLP enrichment pipeline on a cleaned text string.
        """
        return {
            "sentiment": self.analyze_sentiment(text),
            "relevance": self.classify_labels(text, RELEVANCE_LABELS, multi_label=False),
            "user_behaviours": self.classify_labels(text, USER_BEHAVIOURS, multi_label=True, threshold=0.3),
            "purchase_barriers": self.classify_labels(text, PURCHASE_BARRIERS, multi_label=True, threshold=0.3),
            "segments": self.tag_segments(text)
        }
