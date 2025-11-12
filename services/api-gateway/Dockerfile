# syntax=docker/dockerfile:1.7
# API Gateway Service - Optimized Dockerfile
FROM researcher-base:3.11-slim AS base

# Builder stage
FROM base AS builder

# Install build dependencies (if needed for some packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM base AS final

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

WORKDIR /app

# Copy application code (will be overridden by volume in dev)
COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
