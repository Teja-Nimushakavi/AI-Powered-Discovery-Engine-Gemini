"""
Tests for FastAPI endpoints.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@patch("api.main.get_retriever")
@patch("api.main.get_generator")
def test_query_endpoint(mock_get_generator, mock_get_retriever):
    # Mock Retriever
    mock_retriever = mock_get_retriever.return_value
    mock_retriever.retrieve.return_value = [
        {"content": "Great app", "metadata": {"source": "PlayStore"}, "score": 1.5}
    ]
    
    # Mock Generator
    mock_generator = mock_get_generator.return_value
    mock_generator.generate.return_value = "Customers say it's a great app."
    
    response = client.post(
        "/api/v1/query",
        json={"query": "What do customers think?"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["answer"] == "Customers say it's a great app."
    assert len(data["sources"]) == 1
    assert data["sources"][0]["content"] == "Great app"
