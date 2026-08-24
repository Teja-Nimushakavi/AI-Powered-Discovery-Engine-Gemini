# API Reference

The FastAPI backend exposes the RAG engine and system health endpoints.

## Base URL
`http://localhost:8000/api/v1` (or `http://localhost:8080/api/v1` via Docker)

---

## 1. Query Endpoint (RAG)
Executes a hybrid search (semantic + metadata) against the vector database and synthesizes a response using the Gemini LLM.

**Endpoint:** `POST /query`

**Request Body:**
```json
{
  "query": "Why are users abandoning carts on iOS?",
  "top_k": 5
}
```
- `query` (string, required): The natural language question.
- `top_k` (integer, optional): Number of context chunks to retrieve. Default is 5.

**Response (200 OK):**
```json
{
  "answer": "Users are primarily abandoning carts on iOS due to high checkout latency and consistent payment gateway failures.",
  "sources": [
    {
      "content": "The app is unusable on my iPhone. The cart just spins forever.",
      "metadata": {
        "source": "App Store",
        "sentiment": "Negative",
        "date": "2023-10-25"
      }
    }
  ]
}
```

---

## 2. Health Check
Verifies the status of the API and its connection to Postgres, Redis, and ChromaDB.

**Endpoint:** `GET /health`

**Response (200 OK):**
```json
{
  "status": "ok",
  "services": {
    "postgres": "connected",
    "chromadb": "connected",
    "redis": "connected",
    "gemini_api": "configured"
  },
  "timestamp": "2023-10-25T12:00:00Z"
}
```
