"""
Self-contained FastAPI app for Vercel deployment.

Provides a REST surface for the ULTRON Agent backed by hosted Supabase
and OpenAI for live chat responses.

Required environment variables:
  SUPABASE_URL              e.g. https://xxxx.supabase.co
  SUPABASE_ANON_KEY         Public anon JWT
  SUPABASE_SERVICE_ROLE_KEY For writes that need elevated access
  OPENAI_API_KEY            For live AI chat responses
"""

import os
import uuid
import logging
import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SVC_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_KEY = SUPABASE_SVC_KEY or SUPABASE_ANON_KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

_SUPABASE_AVAILABLE = bool(SUPABASE_URL and SUPABASE_KEY)
_OPENAI_AVAILABLE = bool(OPENAI_API_KEY)

# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def _sb_headers(write: bool = False) -> Dict[str, str]:
    key = (SUPABASE_SVC_KEY if write else SUPABASE_ANON_KEY) or SUPABASE_KEY
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


async def _sb_get(table: str, qs: str = "select=*", limit: int = 50) -> List[Dict]:
    if not _SUPABASE_AVAILABLE:
        return []
    url = f"{SUPABASE_URL}/rest/v1/{table}?{qs}"
    if "limit=" not in qs:
        url += f"&limit={limit}"
    async with httpx.AsyncClient(timeout=8) as c:
        r = await c.get(url, headers=_sb_headers())
    if r.status_code == 200:
        return r.json()
    logger.warning("sb GET %s → %s %s", table, r.status_code, r.text[:200])
    return []


async def _sb_post(table: str, data: Dict, write: bool = True) -> Optional[Dict]:
    if not _SUPABASE_AVAILABLE:
        return None
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    async with httpx.AsyncClient(timeout=8) as c:
        r = await c.post(url, headers=_sb_headers(write), json=data)
    if r.status_code in (200, 201):
        rows = r.json()
        return rows[0] if rows else data
    logger.warning("sb POST %s → %s %s", table, r.status_code, r.text[:200])
    return None


async def _sb_patch(table: str, filters: str, data: Dict) -> List[Dict]:
    if not _SUPABASE_AVAILABLE:
        return []
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filters}"
    async with httpx.AsyncClient(timeout=8) as c:
        r = await c.patch(url, headers=_sb_headers(True), json=data)
    if r.status_code == 200:
        return r.json()
    logger.warning("sb PATCH %s → %s %s", table, r.status_code, r.text[:200])
    return []


async def _sb_delete(table: str, filters: str) -> bool:
    if not _SUPABASE_AVAILABLE:
        return False
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filters}"
    async with httpx.AsyncClient(timeout=8) as c:
        r = await c.delete(url, headers=_sb_headers(True))
    return r.status_code in (200, 204)


async def _sb_upsert(table: str, data: Dict, on_conflict: str = "key") -> Optional[Dict]:
    if not _SUPABASE_AVAILABLE:
        return None
    url = f"{SUPABASE_URL}/rest/v1/{table}?on_conflict={on_conflict}"
    h = {**_sb_headers(True), "Prefer": "return=representation,resolution=merge-duplicates"}
    async with httpx.AsyncClient(timeout=8) as c:
        r = await c.post(url, headers=h, json=data)
    if r.status_code in (200, 201):
        rows = r.json()
        return rows[0] if rows else data
    logger.warning("sb UPSERT %s → %s %s", table, r.status_code, r.text[:200])
    return None

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model: str = "gpt-4o-mini"

class ConversationCreateRequest(BaseModel):
    title: str = "New Chat"
    model_name: str = "gpt-4o-mini"
    ai_provider: str = "openai"

class MemoryRequest(BaseModel):
    key: str
    value: Any
    memory_type: str = "long_term"

class ProviderUpdateRequest(BaseModel):
    is_active: Optional[bool] = None
    base_url: Optional[str] = None
    model_list: Optional[str] = None

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ULTRON Agent API",
    description="Cloud REST API for ULTRON Agent — Supabase + OpenAI backend",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Root — serve the Aether Nexus GUI
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the Aether Nexus web GUI."""
    import pathlib
    html_path = pathlib.Path(__file__).parent.parent / "public" / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text())
    return HTMLResponse("<h1>ULTRON Agent API</h1><p>Visit <a href='/docs'>/docs</a></p>")


@app.get("/health")
async def health():
    return JSONResponse({
        "status": "healthy",
        "supabase": "connected" if _SUPABASE_AVAILABLE else "not_configured",
        "openai": "available" if _OPENAI_AVAILABLE else "not_configured",
    })


@app.get("/api/status")
async def api_status():
    return JSONResponse({
        "status": "online",
        "environment": os.getenv("ENV", "production"),
        "supabase_connected": _SUPABASE_AVAILABLE,
        "openai_available": _OPENAI_AVAILABLE,
        "features": ["chat", "memory", "conversations", "providers", "tools", "history"],
        "version": "3.0.0",
    })

# ---------------------------------------------------------------------------
# Chat — backed by OpenAI with Supabase persistence
# ---------------------------------------------------------------------------

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Send a message and get an AI response. Persists to Supabase."""
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conv_id = req.conversation_id

    # Ensure conversation exists
    if not conv_id:
        conv = await _sb_post("conversations", {
            "title": req.message[:60],
            "model_name": req.model,
            "ai_provider": "openai",
            "message_count": 0,
        })
        conv_id = conv["id"] if conv else str(uuid.uuid4())

    # Persist user message
    await _sb_post("messages", {
        "conversation_id": conv_id,
        "role": "user",
        "content": req.message,
    })

    # Fetch recent history for context (last 10 messages)
    history_rows = await _sb_get(
        "messages",
        qs=f"select=role,content&conversation_id=eq.{conv_id}&order=created_at.asc",
        limit=10,
    )

    # Call OpenAI
    ai_reply = ""
    if _OPENAI_AVAILABLE:
        try:
            messages = [
                {"role": "system", "content": (
                    "You are ULTRON, an advanced AI assistant. "
                    "Be helpful, concise, and slightly futuristic in tone."
                )}
            ]
            for row in history_rows[-9:]:
                messages.append({"role": row["role"], "content": row["content"]})

            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}",
                             "Content-Type": "application/json"},
                    json={"model": req.model, "messages": messages, "max_tokens": 1024},
                )
            if r.status_code == 200:
                ai_reply = r.json()["choices"][0]["message"]["content"]
            else:
                logger.warning("OpenAI → %s %s", r.status_code, r.text[:200])
                ai_reply = "⚠️ AI service temporarily unavailable."
        except Exception as exc:
            logger.error("OpenAI error: %s", exc)
            ai_reply = f"⚠️ Error reaching AI: {exc}"
    else:
        ai_reply = "⚠️ OPENAI_API_KEY not configured. Set it in Vercel environment variables."

    # Persist assistant reply
    await _sb_post("messages", {
        "conversation_id": conv_id,
        "role": "assistant",
        "content": ai_reply,
    })

    # Update conversation message_count
    await _sb_patch("conversations", f"id=eq.{conv_id}", {
        "message_count": len(history_rows) + 2,
        "updated_at": ts,
    })

    return JSONResponse({
        "conversation_id": conv_id,
        "reply": ai_reply,
        "model": req.model,
    })

# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

@app.get("/api/conversations")
async def get_conversations(limit: int = 30):
    rows = await _sb_get(
        "conversations",
        qs="select=id,title,model_name,ai_provider,message_count,created_at,updated_at&order=updated_at.desc",
        limit=limit,
    )
    return JSONResponse({"conversations": rows, "count": len(rows)})


@app.post("/api/conversations")
async def create_conversation(req: ConversationCreateRequest):
    row = await _sb_post("conversations", {
        "title": req.title,
        "model_name": req.model_name,
        "ai_provider": req.ai_provider,
        "message_count": 0,
    })
    if not row:
        raise HTTPException(503, "Could not create conversation")
    return JSONResponse(row)


@app.delete("/api/conversations/{conv_id}")
async def delete_conversation(conv_id: str):
    # Delete messages first (FK), then conversation
    await _sb_delete("messages", f"conversation_id=eq.{conv_id}")
    ok = await _sb_delete("conversations", f"id=eq.{conv_id}")
    return JSONResponse({"deleted": ok, "id": conv_id})

# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

@app.get("/api/history")
async def history(conversation_id: Optional[str] = None, limit: int = 50):
    if conversation_id:
        qs = f"select=*&conversation_id=eq.{conversation_id}&order=created_at.asc"
    else:
        qs = "select=*&order=created_at.desc"
    rows = await _sb_get("messages", qs=qs, limit=limit)
    return JSONResponse({"messages": rows, "count": len(rows)})

# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

@app.get("/api/memory")
async def get_memory(limit: int = 100):
    rows = await _sb_get("agent_memory", qs="select=*&order=updated_at.desc", limit=limit)
    return JSONResponse({"entries": rows, "count": len(rows)})


@app.post("/api/memory")
async def save_memory(req: MemoryRequest):
    import json as _json
    val = req.value if isinstance(req.value, dict) else {"data": req.value}
    row = await _sb_upsert("agent_memory", {
        "key": req.key,
        "value": val,
        "memory_type": req.memory_type,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }, on_conflict="key")
    if row is None and not _SUPABASE_AVAILABLE:
        raise HTTPException(503, "Supabase not configured")
    return JSONResponse({"stored": True, "key": req.key, "entry": row})


@app.delete("/api/memory/{key}")
async def delete_memory(key: str):
    from urllib.parse import quote
    ok = await _sb_delete("agent_memory", f"key=eq.{quote(key)}")
    return JSONResponse({"deleted": ok, "key": key})

# ---------------------------------------------------------------------------
# AI Providers
# ---------------------------------------------------------------------------

@app.get("/api/providers")
async def get_providers():
    rows = await _sb_get("ai_providers", qs="select=*&order=provider_name.asc")
    return JSONResponse({"providers": rows, "count": len(rows)})


@app.patch("/api/providers/{provider_id}")
async def update_provider(provider_id: str, req: ProviderUpdateRequest):
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    if not data:
        raise HTTPException(400, "No fields to update")
    data["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rows = await _sb_patch("ai_providers", f"id=eq.{provider_id}", data)
    return JSONResponse({"updated": bool(rows), "provider": rows[0] if rows else None})

# ---------------------------------------------------------------------------
# Tools catalogue (static + from DB)
# ---------------------------------------------------------------------------

BUILTIN_TOOLS = [
    {"name": "LlamaIndex", "category": "AI/LLM", "description": "Unified LLM access, RAG queries, document indexing"},
    {"name": "Supabase Data API", "category": "Database", "description": "Full CRUD on all Supabase tables"},
    {"name": "OpenAI Integration", "category": "AI/LLM", "description": "GPT-4o, DALL-E, Whisper via OpenAI API"},
    {"name": "Amazon Q", "category": "AI/LLM", "description": "AWS Amazon Q developer integration"},
    {"name": "Web Search", "category": "Web", "description": "Search the web via Tor or direct HTTP"},
    {"name": "Screenshot Analyzer", "category": "Vision", "description": "Capture and analyze screenshots with AI"},
    {"name": "Voice Assistant", "category": "Voice", "description": "Speech-to-text and text-to-speech"},
    {"name": "ADB Manager", "category": "Mobile", "description": "Android Debug Bridge for device automation"},
    {"name": "GitHub Integration", "category": "Dev", "description": "Repository management and code review"},
    {"name": "AWS Integration", "category": "Cloud", "description": "S3, Lambda, Bedrock, CodeBuild"},
    {"name": "Azure Automation", "category": "Cloud", "description": "Azure Logic Apps and Functions"},
    {"name": "Google Cloud", "category": "Cloud", "description": "GCP services integration"},
    {"name": "NVIDIA NIM", "category": "AI/LLM", "description": "NVIDIA inference microservices"},
    {"name": "Stable Diffusion", "category": "Vision", "description": "AI image generation"},
    {"name": "AutoGen", "category": "Agents", "description": "Multi-agent orchestration framework"},
    {"name": "Browser MCP", "category": "Web", "description": "Browser automation via Model Context Protocol"},
    {"name": "PyAutoGUI", "category": "Automation", "description": "Desktop GUI automation"},
    {"name": "OCR Tools", "category": "Vision", "description": "Optical character recognition"},
    {"name": "Memory System", "category": "Memory", "description": "Short and long-term semantic memory"},
    {"name": "Task Scheduler", "category": "Automation", "description": "Cron-style task scheduling"},
    {"name": "Ollama", "category": "AI/LLM", "description": "Local LLM inference with Ollama"},
    {"name": "Unity Bridge", "category": "Dev", "description": "Unity game engine integration"},
    {"name": "Avatar Game", "category": "Games", "description": "ULTRON avatar RPG system"},
    {"name": "SSH Server", "category": "System", "description": "Remote SSH access to agent"},
    {"name": "Performance Monitor", "category": "System", "description": "CPU, memory, disk monitoring"},
]


@app.get("/api/tools")
async def get_tools():
    return JSONResponse({"tools": BUILTIN_TOOLS, "count": len(BUILTIN_TOOLS)})

# ---------------------------------------------------------------------------
# Tool executions log
# ---------------------------------------------------------------------------

@app.get("/api/tool-executions")
async def get_tool_executions(limit: int = 50):
    rows = await _sb_get(
        "tool_executions",
        qs="select=tool_name,status,duration_ms,created_at&order=created_at.desc",
        limit=limit,
    )
    return JSONResponse({"executions": rows, "count": len(rows)})

# ---------------------------------------------------------------------------
# System status
# ---------------------------------------------------------------------------

@app.get("/api/system")
async def system_status():
    """Return cloud-side system status (Supabase + OpenAI health)."""
    sb_ok = _SUPABASE_AVAILABLE
    oai_ok = _OPENAI_AVAILABLE

    # Count rows in key tables as a health signal
    mem_count = 0
    conv_count = 0
    if sb_ok:
        try:
            rows = await _sb_get("agent_memory", qs="select=id", limit=1000)
            mem_count = len(rows)
            rows2 = await _sb_get("conversations", qs="select=id", limit=1000)
            conv_count = len(rows2)
        except Exception:
            pass

    return JSONResponse({
        "supabase": {"status": "online" if sb_ok else "offline", "url": SUPABASE_URL or None},
        "openai": {"status": "available" if oai_ok else "not_configured"},
        "memory_entries": mem_count,
        "conversations": conv_count,
        "version": "3.0.0",
        "deployment": "vercel",
    })

