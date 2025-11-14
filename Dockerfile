# ULTRON Agent 3.0 - Production Docker Image
# Multi-stage build for optimized image size and security
# Base: Python 3.10-slim (minimal, secure)

# Stage 1: Builder - Install dependencies
FROM python:3.10-slim as builder

LABEL maintainer="ULTRON Agent Development Team"
LABEL description="ULTRON Agent 3.0 - Multi-modal AI Assistant Platform"
LABEL version="3.0.0"

# Set environment variables for build stage
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Stage 2: Runtime - Minimal production image
FROM python:3.10-slim

# Metadata
LABEL maintainer="ULTRON Agent Development Team"
LABEL description="ULTRON Agent 3.0 - Production Runtime"
LABEL version="3.0.0"

# Set environment variables for runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    ULTRON_ENVIRONMENT="production" \
    OLLAMA_BASE_URL="http://ollama:11434" \
    API_PORT="5000" \
    WEB_GUI_PORT="8080" \
    CHAT_PORT="8000"

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 ultron && \
    mkdir -p /app /app/logs && \
    chown -R ultron:ultron /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code (with proper permissions)
COPY --chown=ultron:ultron . .

# Create necessary directories with proper permissions
RUN mkdir -p logs gui/ultron_enhanced/web && \
    chmod -R 755 logs && \
    chmod +x main.py

# Switch to non-root user
USER ultron

# Health check endpoint for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${API_PORT}/health || exit 1

# Expose all service ports
EXPOSE 5000 8000 8080 11434

# Production startup command
CMD ["python", "main.py"]
