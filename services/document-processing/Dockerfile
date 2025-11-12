# syntax=docker/dockerfile:1.7
# Document Processing Service - Optimized Dockerfile
FROM researcher-base:3.11-slim AS base

# Builder stage
FROM base AS builder

# Install build dependencies and PDF/OCR tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
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

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create necessary directories with correct permissions
RUN mkdir -p /app/uploads && chown -R appuser:appuser /app

# Copy entrypoint script
COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to non-root user
USER appuser

WORKDIR /app

# Copy application code (will be overridden by volume in dev)
COPY --chown=appuser:appuser . .

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
