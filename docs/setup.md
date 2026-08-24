# Setup & Development Guide

This guide covers setting up the RAG Discovery Engine for local development.

## 1. Prerequisites
- **Python 3.11+**
- **Node.js 20+**
- **Docker & Docker Compose**
- **Gemini API Key** (for the LLM)

## 2. Environment Variables
Copy the `.env.example` file to `.env` in the root directory:
```bash
cp .env.example .env
```
Ensure you fill in your `GOOGLE_API_KEY`. The default database URLs are configured to work seamlessly with the local Docker containers.

## 3. Starting the Databases
We recommend running the databases via Docker, even if you are running the API and Frontend natively for development.
```bash
docker compose up -d postgres chromadb redis
```

## 4. Running the Backend (FastAPI)
Create a Python virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Start the API:
```bash
uvicorn api.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. Swagger UI docs are at `/docs`.

## 5. Running the Frontend (React)
Navigate to the frontend directory:
```bash
cd frontend
npm install
npm run dev
```
The UI will be available at `http://localhost:5173`.

## 6. Running the Scraper Pipeline
To ingest new data and compute embeddings:
```bash
python run_scrapers.py --all
```
This will fetch reviews, clean them, insert metadata into Postgres, and index embeddings into ChromaDB.
