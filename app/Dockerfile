# =============================================================================
# Dockerfile for Streamlit Dashboard
# Project: Music Events Data Pipeline
# Base: python:3.12-slim
# =============================================================================

FROM python:3.12-slim

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements-app.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-app.txt

# Copy application source code
COPY app.py .

# Create log directory (app.py writes logs to /app/logs/)
RUN mkdir -p /app/logs

# Expose Streamlit default port
EXPOSE 8501

# Health check — Streamlit serves a /_stcore/health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the Streamlit app
# --server.address=0.0.0.0  : accept connections from outside the container
# --server.headless=true    : disable browser auto-open (required in Docker)
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
