"""
FastAPI application for the RAG Discovery Engine.
"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag.retriever import HybridRetriever
from rag.generator import AnswerGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Myntra RAG Discovery Engine",
    description="API for querying consumer feedback insights via RAG.",
    version="1.0.0"
)

# Add CORS middleware to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy initialization of RAG components
_retriever: HybridRetriever | None = None
_generator: AnswerGenerator | None = None


def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


def get_generator() -> AnswerGenerator:
    global _generator
    if _generator is None:
        _generator = AnswerGenerator()
    return _generator


class QueryRequest(BaseModel):
    query: str
    metadata_filter: dict[str, Any] | None = None
    top_k: int = 10


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]]


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/v1/query", response_model=QueryResponse)
def query_rag(request: QueryRequest) -> QueryResponse:
    """
    Query the RAG pipeline.
    """
    logger.info("Received query: %s", request.query)
    
    try:
        retriever = get_retriever()
        generator = get_generator()
        
        # 1. Retrieve
        chunks = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            metadata_filter=request.metadata_filter
        )
        
        if not chunks:
            return QueryResponse(
                answer="I couldn't find any relevant feedback to answer your question.",
                sources=[]
            )
            
        # 2. Generate
        answer = generator.generate(request.query, chunks)
        
        return QueryResponse(answer=answer, sources=chunks)
        
    except Exception as e:
        logger.error("RAG pipeline failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
