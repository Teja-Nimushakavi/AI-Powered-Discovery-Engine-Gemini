"""
Vector DB Indexer for the RAG Discovery Engine.

Handles text chunking (LangChain) and insertion into ChromaDB
using local embedding models (BGE).
"""

from __future__ import annotations

import logging
from typing import Any

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class VectorIndexer:
    """
    Manages indexing of enriched feedback records into ChromaDB.
    """

    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 8000, 
        collection_name: str = "feedback_embeddings"
    ) -> None:
        """Initialize ChromaDB client and embedding function."""
        logger.info("Initializing Vector Indexer...")
        
        # We try to connect to the HTTP client (Docker), fallback to PersistentClient if unavailable
        try:
            self.client = chromadb.HttpClient(host=host, port=port)
            self.client.heartbeat()
            logger.info("Connected to ChromaDB via HTTP at %s:%s", host, port)
        except Exception:
            logger.warning("Could not connect to ChromaDB HTTP client. Falling back to local PersistentClient.")
            self.client = chromadb.PersistentClient(path="./chroma_data")
            
        # Using BAAI/bge-large-en-v1.5 as per architecture, but falling back to small for speed in dev
        self.embedding_function = SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-en-v1.5")
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Myntra Consumer Feedback RAG Index"}
        )
        
        # Setup Text Splitter
        # Chunk at paragraph/sentence level to preserve citation granularity
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""]
        )

    def index_record(self, record: dict[str, Any]) -> None:
        """
        Chunks the cleaned text and indexes it into ChromaDB with rich metadata.
        """
        text = record.get("content_cleaned", "")
        if not text:
            return
            
        feedback_id = record["feedback_id"]
        
        # Generate chunks
        chunks = self.text_splitter.split_text(text)
        
        if not chunks:
            return
            
        ids = [f"{feedback_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Prepare metadata payload
        # ChromaDB requires metadata values to be str, int, float or bool
        frictions = record.get("frictions", [])
        friction_labels = ",".join([f["label"] for f in frictions]) if frictions else ""
        
        sentiment = record.get("sentiment", {})
        sentiment_label = sentiment.get("label", "neutral")
        
        segments = record.get("segments", [])
        segment_tags = ",".join(segments) if segments else ""
        
        metadatas = []
        for _ in chunks:
            metadatas.append({
                "feedback_id": feedback_id,
                "source": record.get("source", ""),
                "source_url": record.get("source_url", ""),
                "author_id_hash": record.get("author_id_hash", ""),
                "timestamp": str(record.get("timestamp", "")),
                "sentiment": sentiment_label,
                "frictions": friction_labels,
                "segments": segment_tags,
            })
            
        # Add to ChromaDB
        try:
            self.collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            logger.debug("Indexed %d chunks for record %s", len(chunks), feedback_id)
        except Exception as e:
            logger.error("Failed to index record %s: %s", feedback_id, e)
