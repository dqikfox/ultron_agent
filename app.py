#!/usr/bin/env python3
"""
ULTRON Agent FastAPI Application Entry Point for Vercel Deployment
"""

import os
import sys
import logging
from typing import Optional

# Set up logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import and create the FastAPI app
try:
    # Try to import from simple_server first
    from simple_server import app
    logger.info("✅ Successfully imported FastAPI app from simple_server.py")
except ImportError as e:
    logger.error(f"Failed to import from simple_server: {e}")
    # Fallback: create a minimal FastAPI app
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI(
        title="ULTRON Agent API",
        description="Local voice-first AI assistant with multi-model support",
        version="3.0.0"
    )

    @app.get("/")
    async def root():
        """Health check endpoint"""
        return JSONResponse({
            "status": "ok",
            "message": "ULTRON Agent API is running",
            "version": "3.0.0"
        })

    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return JSONResponse({"status": "healthy"})

    logger.warning("⚠️ Using fallback FastAPI app (simple_server not available)")

# Ensure the app is properly exported for Vercel
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    logger.info(f"🚀 Starting ULTRON Agent API on {host}:{port}")

    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=os.getenv("ENV", "development") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
