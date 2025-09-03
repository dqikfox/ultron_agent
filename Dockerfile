# Multi-stage Dockerfile for ULTRON Agent
FROM python:3.10-slim as builder

# Set build arguments
ARG VERSION
ARG BUILD_DATE
ARG BUILD_COMMIT

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up Python build environment
WORKDIR /build
COPY pyproject.toml requirements.txt ./
COPY ultron_agent/ ./ultron_agent/
COPY *.py ./

# Install Python dependencies and build package
RUN pip install --no-cache-dir --upgrade pip build
RUN python -m build --wheel

# Production stage
FROM python:3.10-slim

# Set labels for metadata
LABEL org.opencontainers.image.title="ULTRON Agent"
LABEL org.opencontainers.image.description="Local voice-first AI assistant with multi-model support"
LABEL org.opencontainers.image.source="https://github.com/dqikfox/ultron_agent"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${BUILD_COMMIT}"

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    pulseaudio \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r ultron && useradd -r -g ultron ultron

# Set up application directory
WORKDIR /app
RUN chown ultron:ultron /app

# Copy built wheel from builder stage
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl

# Copy configuration and startup scripts
COPY ultron_config.json.example /app/ultron_config.json
COPY --chown=ultron:ultron scripts/docker-entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create directories for data persistence
RUN mkdir -p /app/logs /app/cache /app/data && \
    chown -R ultron:ultron /app/logs /app/cache /app/data

# Switch to non-root user
USER ultron

# Set environment variables
ENV PYTHONPATH=/app
ENV ULTRON_CONFIG_FILE=/app/ultron_config.json
ENV ULTRON_LOG_LEVEL=INFO
ENV ULTRON_HOST=0.0.0.0
ENV ULTRON_PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${ULTRON_PORT}/health || exit 1

# Expose port
EXPOSE 8000

# Volume for persistent data
VOLUME ["/app/logs", "/app/cache", "/app/data"]

# Entry point
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["ultron", "serve"]