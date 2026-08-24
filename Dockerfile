# =============================================================================
# Dockerfile — AI-Powered RAG Discovery Engine (Hugging Face Spaces)
# =============================================================================

FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (Hugging Face runs as user 1000)
RUN useradd -m -u 1000 user

# Install Python dependencies
COPY requirements_api.txt .
RUN pip install --no-cache-dir -r requirements_api.txt

# Copy application source
COPY . .

# Set permissions for the data directories so user 1000 can read/write them
RUN chown -R user:user /app

# Switch to non-root user
USER user

# Expose Hugging Face's required port
EXPOSE 7860

# Run FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
