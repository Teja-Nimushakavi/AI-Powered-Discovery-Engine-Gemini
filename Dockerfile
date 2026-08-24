# =============================================================================
# Dockerfile — AI-Powered RAG Discovery Engine
# =============================================================================
# Multi-stage build for the Python application
# =============================================================================

FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home appuser

WORKDIR /app

# ── Install Python dependencies ───────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application source ───────────────────────────────────────────
COPY . .

# Create data directories
RUN mkdir -p data/raw && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Default command — can be overridden
CMD ["python", "run_scrapers.py", "--all"]
