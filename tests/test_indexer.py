"""
Tests for Vector DB Indexer.
"""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest
from vectordb.indexer import VectorIndexer


@pytest.fixture
def mock_indexer():
    """Returns a VectorIndexer with mocked ChromaDB and Embedding models."""
    with patch("vectordb.indexer.chromadb.HttpClient") as mock_http_client, \
         patch("vectordb.indexer.SentenceTransformerEmbeddingFunction") as mock_embedding:
        
        mock_client_instance = MagicMock()
        mock_http_client.return_value = mock_client_instance
        
        mock_collection = MagicMock()
        mock_client_instance.get_or_create_collection.return_value = mock_collection
        
        indexer = VectorIndexer()
        # Expose the mock collection for assertions
        indexer.mock_collection = mock_collection 
        return indexer


def test_index_record_chunking_and_metadata(mock_indexer):
    # Create a dummy record
    record = {
        "feedback_id": "rec_123",
        "content_cleaned": "This is a very long text. " * 50,
        "source": "app_store",
        "source_url": "http://example.com",
        "author_id_hash": "hash123",
        "timestamp": "2023-10-01",
        "sentiment": {"label": "positive", "score": 0.9},
        "frictions": [{"label": "fit ambiguity", "score": 0.8}],
        "segments": ["Gen Z"]
    }
    
    # We force the chunk size very small to guarantee it splits
    mock_indexer.text_splitter.chunk_size = 20
    mock_indexer.text_splitter.chunk_overlap = 0
    
    mock_indexer.index_record(record)
    
    # Verify add was called
    mock_indexer.mock_collection.add.assert_called_once()
    
    # Inspect arguments passed to add
    _, kwargs = mock_indexer.mock_collection.add.call_args
    
    chunks = kwargs["documents"]
    metadatas = kwargs["metadatas"]
    ids = kwargs["ids"]
    
    assert len(chunks) > 1
    assert len(chunks) == len(metadatas) == len(ids)
    
    # Check ID format
    assert ids[0] == "rec_123_chunk_0"
    
    # Check Metadata structure
    meta = metadatas[0]
    assert meta["feedback_id"] == "rec_123"
    assert meta["sentiment"] == "positive"
    assert meta["frictions"] == "fit ambiguity"
    assert meta["segments"] == "Gen Z"
    assert meta["source"] == "app_store"


def test_index_record_empty(mock_indexer):
    mock_indexer.index_record({"feedback_id": "rec_000", "content_cleaned": ""})
    mock_indexer.mock_collection.add.assert_not_called()
