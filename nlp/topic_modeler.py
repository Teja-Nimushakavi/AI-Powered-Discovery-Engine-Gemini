"""
Topic Modeler for the RAG Discovery Engine.

Uses BERTopic to discover emerging themes and friction points
from the feedback corpus over time.
"""

from __future__ import annotations

import logging
from typing import Any

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer

logger = logging.getLogger(__name__)


class TopicModeler:
    """
    Wraps BERTopic for unsupervised topic modeling.
    """

    def __init__(self, embedding_model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        """
        Initialize the BERTopic model with its component sub-models.
        """
        logger.info("Initializing Topic Modeler...")
        
        # 1. Embedding Model (using sentence-transformers)
        # Using a smaller model by default for speed, but BGE is very strong
        self.embedding_model = SentenceTransformer(embedding_model_name)
        
        # 2. Dimensionality Reduction (UMAP)
        # Random state set for reproducibility
        self.umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine", random_state=42)
        
        # 3. Clustering (HDBSCAN)
        self.hdbscan_model = HDBSCAN(min_cluster_size=10, metric="euclidean", cluster_selection_method="eom")
        
        # 4. Vectorizer (removing English stop words)
        self.vectorizer_model = CountVectorizer(stop_words="english", ngram_range=(1, 2))
        
        # Build BERTopic
        self.topic_model = BERTopic(
            embedding_model=self.embedding_model,
            umap_model=self.umap_model,
            hdbscan_model=self.hdbscan_model,
            vectorizer_model=self.vectorizer_model,
            language="english",
            calculate_probabilities=False,
            verbose=True
        )
        logger.info("Topic Modeler initialized.")

    def fit_transform(self, docs: list[str]) -> tuple[list[int], list[dict[str, Any]]]:
        """
        Run topic modeling on a list of text documents.
        Returns the topics for each document, and information about the clusters.
        """
        if len(docs) < 10:
            logger.warning("Not enough documents for BERTopic (needs at least 10).")
            return [0] * len(docs), []
            
        topics, _ = self.topic_model.fit_transform(docs)
        
        # Extract topic info
        topic_info = self.topic_model.get_topic_info()
        
        clusters = []
        for _, row in topic_info.iterrows():
            topic_id = int(row["Topic"])
            if topic_id == -1:
                continue # Outliers
                
            # Get keywords for the topic
            keywords_raw = self.topic_model.get_topic(topic_id)
            if keywords_raw:
                keywords = {kw: float(weight) for kw, weight in keywords_raw}
            else:
                keywords = {}
                
            clusters.append({
                "cluster_id": topic_id,
                "cluster_label": row["Name"],
                "record_count": int(row["Count"]),
                "keywords": keywords
            })
            
        return topics, clusters
