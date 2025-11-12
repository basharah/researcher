# syntax=docker/dockerfile:1.7
# Vector DB Service - Optimized Dockerfile with CUDA support
FROM researcher-base:3.11-slim AS base

# Builder stage
FROM base AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install PyTorch with CUDA support (smaller CUDA runtime, not full toolkit)
RUN pip install --no-cache-dir torch==2.2.0+cu121 --index-url https://download.pytorch.org/whl/cu121

# Copy and install remaining requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM base AS final

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set Hugging Face cache directory to writable location
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/transformers

# Set ownership and create cache directory
RUN mkdir -p /app/.cache && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

WORKDIR /app

# Copy application code (will be overridden by volume in dev)
COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
