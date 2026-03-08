"""
Self-contained FastAPI app for Vercel deployment.

Provides a REST surface for the ULTRON Agent backed by a hosted Supabase
project. Heavy local dependencies (torch, agent_core, voice, etc.) are
intentionally absent — this is the cloud-facing API layer only.

Required environment variables (set via `npx vercel env add`):
  SUPABASE_URL       e.g. https://xxxx.supabase.co
  SUPABASE_ANON_KEY  Public anon JWT from Supabase project settings

Optional:
  SUPABASE_SERVICE_ROLE_KEY  For write operations that need elevated access
  LOG_LEVEL                  Default: info
  ENV                        Default: production
"""

import os
import logging
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supabase REST helpers
# ---------------------------------------------------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

_SUPABASE_AVAILABLE = bool(SUPABASE_URL and SUPABASE_KEY)


def _headers() -> Dict[str, str]:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


async def _sb_get(table: str, qs: str = "select=*", limit: int = 50) -> List[Dict]:
    """Fetch rows from a Supabase table."""
    if not _SUPABASE_AVAILABLE:
        return []
    url = f"{SUPABASE_URL}/rest/v1/{table}?{qs}&limit={limit}"
    async with httpx.AsyncClient(timeout=8) as client:
        r = await client.get(url, headers=_headers())
    if r.status_code == 200:
        return r.json()
    logger.warning("Supabase GET %s → %s %s", table, r.status_code, r.text[:200])
    return []


async def _sb_post(table: str, data: Dict) -> Optional[Dict]:
    """Insert a row and return the created record."""
    if not _SUPABASE_AVAILABLE:
        return None
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    async with httpx.AsyncClient(timeout=8) as client:
        r = await client.post(url, headers=_headers(), json=data)
    if r.status_code in (200, 201):
        rows = r.json()
        return rows[0] if rows else data
    logger.warning("Supabase POST %s → %s %s", table, r.status_code, r.text[:200])
    return None


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    session_id: Optional[str] = None


class MemoryRequest(BaseModel):
    key: str
    value: Any
    category: str = "general"


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ULTRON Agent API",
    description="Cloud-facing REST API for the ULTRON Agent — backed by Supabase",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return JSONResponse({
        "status": "ok",
        "message": "ULTRON Agent API is running",
        "version": "3.0.0",
        "docs": "/docs",
        "supabase_connected": _SUPABASE_AVAILABLE,
    })


@app.get("/health")
async def health():
    sb_status = "connected" if _SUPABASE_AVAILABLE else "not_configured"
    return JSONResponse({"status": "healthy", "service": "ultron-agent", "supabase": sb_status})


@app.get("/api/status")
async def api_status():
    return JSONResponse({
        "status": "online",
        "environment": os.getenv("ENV", "production"),
        "supabase_url": SUPABASE_URL or None,
        "supabase_connected": _SUPABASE_AVAILABLE,
        "features": ["chat", "memory", "history", "providers"],
    })


# ---------------------------------------------------------------------------
# Chat endpoints
# ---------------------------------------------------------------------------

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    Accept a user message and persist it.
    In full deployment this would proxy to the local Ollama agent;
    here it stores the message and returns an acknowledgement.
    """
    import uuid, datetime

    conv_id = req.conversation_id or str(uuid.uuid4())
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Persist user message
    await _sb_post("messages", {
        "id": str(uuid.uuid4()),
        "conversation_id": conv_id,
        "role": "user",
        "content": req.message,
        "created_at": ts,
    })

    return JSONResponse({
        "conversation_id": conv_id,
        "status": "received",
        "message": "Message stored. Connect a local ULTRON agent to process replies.",
        "persisted": _SUPABASE_AVAILABLE,
    })


@app.get("/api/history")
async def history(conversation_id: Optional[str] = None, limit: int = 20):
    """Return recent messages, optionally filtered by conversation."""
    if conversation_id:
        qs = f"select=*&conversation_id=eq.{conversation_id}&order=created_at.desc"
    else:
        qs = "select=*&order=created_at.desc"
    rows = await _sb_get("messages", qs=qs, limit=limit)
    return JSONResponse({"messages": rows, "count": len(rows)})


@app.get("/api/conversations")
async def conversations(limit: int = 20):
    """Return recent conversations."""
    rows = await _sb_get("conversations", qs="select=*&order=created_at.desc", limit=limit)
    return JSONResponse({"conversations": rows, "count": len(rows)})


# ---------------------------------------------------------------------------
# Memory endpoints
# ---------------------------------------------------------------------------

@app.get("/api/memory")
async def get_memory(category: Optional[str] = None):
    """Return stored agent memory entries."""
    qs = "select=*&order=created_at.desc"
    if category:
        qs += f"&category=eq.{category}"
    rows = await _sb_get("agent_memory", qs=qs, limit=100)
    return JSONResponse({"entries": rows, "count": len(rows)})


@app.post("/api/memory")
async def save_memory(req: MemoryRequest):
    """Store a memory entry."""
    import uuid, json as _json, datetime
    row = await _sb_post("agent_memory", {
        "id": str(uuid.uuid4()),
        "key": req.key,
        "value": _json.dumps(req.value) if not isinstance(req.value, str) else req.value,
        "category": req.category,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })
    if row is None and not _SUPABASE_AVAILABLE:
        raise HTTPException(503, "Supabase not configured — set SUPABASE_URL and SUPABASE_ANON_KEY")
    return JSONResponse({"stored": True, "key": req.key})


# ---------------------------------------------------------------------------
# AI providers
# ---------------------------------------------------------------------------

@app.get("/api/providers")
async def providers():
    """Return configured AI providers from Supabase."""
    rows = await _sb_get("ai_providers", qs="select=*&order=provider_name.asc")
    return JSONResponse({"providers": rows, "count": len(rows)})
