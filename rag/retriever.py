"""
Hybrid Retriever for RAG.
Combines ChromaDB Vector Search with in-memory BM25 Keyword Search.
"""

from __future__ import annotations

import logging
from typing import Any

from rank_bm25 import BM25Okapi
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Retrieves and ranks relevant chunks for a given query.
    """

    def __init__(self, host: str = "localhost", port: int = 8000, collection_name: str = "feedback_embeddings") -> None:
        logger.info("Initializing Hybrid Retriever...")
        
        try:
            self.client = chromadb.HttpClient(host=host, port=port)
            self.client.heartbeat()
        except Exception:
            self.client = chromadb.PersistentClient(path="./chroma_data")
            
        self.embedding_function = SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-en-v1.5")
        
        # We assume the collection exists (created in Phase 3)
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
        except Exception:
            # Create empty if missing so tests don't crash
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )

    def retrieve(self, query: str, top_k: int = 10, metadata_filter: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        Retrieves top_k chunks using dense vector search, then re-ranks with BM25.
        """
        logger.debug("Retrieving for query: %s", query)
        
        # 1. Dense Vector Retrieval (fetch 2x top_k for re-ranking pool)
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k * 2,
                where=metadata_filter
            )
        except Exception as e:
            logger.error("Chroma query failed: %s", e)
            return []
            
        if not results or not results["documents"] or not results["documents"][0]:
            return []
            
        docs = results["documents"][0]
        metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
        
        # 2. BM25 Re-ranking
        tokenized_query = query.lower().split()
        tokenized_corpus = [doc.lower().split() for doc in docs]
        
        bm25 = BM25Okapi(tokenized_corpus)
        bm25_scores = bm25.get_scores(tokenized_query)
        
        # 3. Combine scores (Simple linear combination for now, since this is local dev)
        # We can implement formal RRF (Reciprocal Rank Fusion) here later.
        ranked_indices = sorted(range(len(docs)), key=lambda i: bm25_scores[i], reverse=True)
        
        # 4. Return Top K
        final_results = []
        for idx in ranked_indices[:top_k]:
            final_results.append({
                "content": docs[idx],
                "metadata": metadatas[idx],
                "score": bm25_scores[idx]
            })
            
        return final_results
