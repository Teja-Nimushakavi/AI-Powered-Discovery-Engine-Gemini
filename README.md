# AI-Powered RAG Discovery Engine

Welcome to the AI-Powered RAG Discovery Engine! This platform is designed to ingest raw consumer feedback from multiple sources (App Store, Play Store, Helpdesk), clean and process it using NLP, index it into a Vector Database, and provide an interactive AI dashboard to query insights using Natural Language.

## Architecture

The system is built on a modern, decoupled architecture:
1. **Scrapers & Data Pipelines**: Python scripts that fetch data from app stores and internal sources, dumping them into a local datalake (`data/raw/`).
2. **NLP Engine**: Cleans text, analyzes sentiment (VADER/Transformers), extracts friction points, and calculates embeddings using `SentenceTransformers`.
3. **Storage Layer**:
   - **PostgreSQL**: Stores structured metadata, source details, and raw text.
   - **ChromaDB**: Stores dense vector embeddings for semantic search.
   - **Redis**: Caching layer for frequent queries to reduce LLM costs.
4. **API Backend**: A FastAPI application providing the `/api/v1/query` endpoint which orchestrates the Hybrid Search (Vector + Keyword) and calls the Gemini LLM for synthesis.
5. **Frontend Dashboard**: A responsive, glassmorphic React/Vite dashboard powered by TailwindCSS to visualize metrics, sentiment timelines, and interact with the RAG engine.

## Quick Start (Docker)

The fastest way to deploy the entire stack is via Docker Compose.

### Prerequisites
- Docker and Docker Compose installed.
- A Gemini API Key (`GOOGLE_API_KEY`).

### Steps
1. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

2. **Start the Infrastructure:**
   ```bash
   docker compose up -d
   ```
   This will spin up:
   - PostgreSQL (Port 5432)
   - ChromaDB (Port 8000)
   - Redis (Port 6379)
   - FastAPI Backend (Port 8080)
   - React Frontend (Port 80)

3. **Access the Dashboard:**
   Open your browser and navigate to `http://localhost`.

## Documentation
For detailed setup instructions, API references, and development guides, please check the `/docs` directory:
- [Setup Guide](docs/setup.md)
- [API Reference](docs/api_reference.md)
