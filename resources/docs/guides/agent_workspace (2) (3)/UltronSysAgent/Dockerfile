# UltronSysAgent Docker Container
# Note: This is primarily for development and testing
# Full functionality requires Windows host system

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    portaudio19-dev \
    python3-pyaudio \
    tesseract-ocr \
    tesseract-ocr-eng \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data/{memory,cache,models} plugins

# Set environment variables
ENV PYTHONPATH=/app
ENV ULTRON_OFFLINE_MODE=true
ENV ULTRON_GUI_ENABLED=false

# Expose ports for web interface (if implemented)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "main.py"]

# Build instructions:
# docker build -t ultron-sys-agent .
# 
# Run instructions:
# docker run -it --rm \
#   -v $(pwd)/config:/app/config \
#   -v $(pwd)/data:/app/data \
#   -v $(pwd)/logs:/app/logs \
#   -p 8080:8080 \
#   --name ultron-agent \
#   ultron-sys-agent
