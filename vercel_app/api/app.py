"""
Minimal self-contained FastAPI app for Vercel deployment.
No heavy local dependencies (torch, agent_core, etc.) required.
"""
import os
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ULTRON Agent API",
    description="Local voice-first AI assistant with multi-model support",
    version="3.0.0",
)


@app.get("/")
async def root():
    return JSONResponse({
        "status": "ok",
        "message": "ULTRON Agent API is running",
        "version": "3.0.0",
        "docs": "/docs",
    })


@app.get("/health")
async def health():
    return JSONResponse({"status": "healthy", "service": "ultron-agent"})


@app.get("/api/status")
async def api_status():
    return JSONResponse({
        "status": "online",
        "environment": os.getenv("ENV", "production"),
        "features": ["chat", "memory", "tools"],
    })
