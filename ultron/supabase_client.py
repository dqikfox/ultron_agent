"""
Async Supabase REST API client for ULTRON Agent.

Wraps PostgREST endpoints so the agent can read/write all Supabase
tables without the supabase-py library. Falls back gracefully if the
local stack is unavailable.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)

# Tables this client manages
TABLES = ("profiles", "conversations", "messages", "ai_providers",
          "file_uploads", "tool_executions")


class SupabaseClient:
    """Thin async REST wrapper around a local (or remote) Supabase project."""

    def __init__(self, url: str, service_role_key: str):
        self.base_url = url.rstrip("/")
        self.key = service_role_key
        self._session: Optional[aiohttp.ClientSession] = None
        self.available = False
        self.current_conversation_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> bool:
        """Open HTTP session and verify reachability. Returns True on success."""
        try:
            self._session = aiohttp.ClientSession(
                headers={
                    "apikey": self.key,
                    "Authorization": f"Bearer {self.key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                timeout=aiohttp.ClientTimeout(total=5),
            )
            # Quick health-check via REST root
            async with self._session.get(f"{self.base_url}/rest/v1/") as resp:
                self.available = resp.status == 200
                if self.available:
                    logger.info("SupabaseClient: connected to %s", self.base_url)
                else:
                    logger.warning("SupabaseClient: unexpected status %s", resp.status)
        except Exception as exc:
            logger.warning("SupabaseClient: unavailable — %s", exc)
            self.available = False
        return self.available

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    # ------------------------------------------------------------------
    # Generic CRUD helpers
    # ------------------------------------------------------------------

    def _url(self, table: str, filters: str = "") -> str:
        base = f"{self.base_url}/rest/v1/{table}"
        return f"{base}?{filters}" if filters else base

    async def select(self, table: str, filters: str = "select=*",
                     limit: int = 100) -> List[Dict]:
        """SELECT rows. filters is a raw PostgREST query string."""
        if not self.available or not self._session:
            return []
        qs = f"{filters}&limit={limit}" if "limit=" not in filters else filters
        try:
            async with self._session.get(self._url(table, qs)) as resp:
                if resp.status == 200:
                    return await resp.json()
                logger.warning("select %s → %s", table, resp.status)
        except Exception as exc:
            logger.warning("select %s failed: %s", table, exc)
        return []

    async def insert(self, table: str, data: Dict) -> Optional[Dict]:
        """INSERT a row and return it."""
        if not self.available or not self._session:
            return None
        try:
            async with self._session.post(self._url(table),
                                          json=data) as resp:
                if resp.status in (200, 201):
                    rows = await resp.json()
                    return rows[0] if rows else None
                body = await resp.text()
                logger.warning("insert %s → %s: %s", table, resp.status, body)
        except Exception as exc:
            logger.warning("insert %s failed: %s", table, exc)
        return None

    async def update(self, table: str, filters: str,
                     data: Dict) -> List[Dict]:
        """UPDATE rows matching filters."""
        if not self.available or not self._session:
            return []
        try:
            async with self._session.patch(self._url(table, filters),
                                           json=data) as resp:
                if resp.status == 200:
                    return await resp.json()
                logger.warning("update %s → %s", table, resp.status)
        except Exception as exc:
            logger.warning("update %s failed: %s", table, exc)
        return []

    async def delete(self, table: str, filters: str) -> bool:
        """DELETE rows matching filters."""
        if not self.available or not self._session:
            return False
        try:
            async with self._session.delete(self._url(table, filters)) as resp:
                return resp.status in (200, 204)
        except Exception as exc:
            logger.warning("delete %s failed: %s", table, exc)
        return False

    async def upsert(self, table: str, data: Dict,
                     on_conflict: str = "id") -> Optional[Dict]:
        """INSERT … ON CONFLICT DO UPDATE."""
        if not self.available or not self._session:
            return None
        headers_extra = {"Prefer": "return=representation,resolution=merge-duplicates"}
        url = self._url(table, f"on_conflict={on_conflict}")
        try:
            async with self._session.post(
                url,
                json=data,
                headers=headers_extra,
            ) as resp:
                if resp.status in (200, 201):
                    rows = await resp.json()
                    return rows[0] if rows else None
                body = await resp.text()
                logger.warning("upsert %s → %s: %s", table, resp.status, body)
        except Exception as exc:
            logger.warning("upsert %s failed: %s", table, exc)
        return None

    # ------------------------------------------------------------------
    # High-level agent helpers
    # ------------------------------------------------------------------

    async def start_conversation(self, title: str = "ULTRON Session",
                                  model_name: str = "local",
                                  ai_provider: str = "ollama") -> Optional[str]:
        """Create a new conversation row and store its id."""
        row = await self.insert("conversations", {
            "title": title,
            "model_name": model_name,
            "ai_provider": ai_provider,
            "message_count": 0,
        })
        if row:
            self.current_conversation_id = row["id"]
            logger.info("SupabaseClient: conversation started → %s",
                        self.current_conversation_id)
        return self.current_conversation_id

    async def persist_message(self, conversation_id: Optional[str],
                               role: str, content: str,
                               processing_time_ms: int = 0,
                               tokens_used: int = 0) -> Optional[str]:
        """Save a single message and increment conversation counter."""
        cid = conversation_id or self.current_conversation_id
        if not cid:
            return None

        row = await self.insert("messages", {
            "conversation_id": cid,
            "role": role,
            "content": content,
            "processing_time_ms": processing_time_ms,
            "tokens_used": tokens_used,
        })

        # Keep conversation message_count in sync
        conv_rows = await self.select("conversations",
                                      f"select=message_count&id=eq.{cid}")
        if conv_rows:
            new_count = (conv_rows[0].get("message_count") or 0) + 1
            await self.update("conversations", f"id=eq.{cid}",
                              {"message_count": new_count,
                               "updated_at": datetime.now(timezone.utc).isoformat()})

        return row["id"] if row else None

    async def log_tool_execution(self, tool_name: str, input_text: str,
                                  output_text: Any, status: str = "success",
                                  duration_ms: int = 0) -> None:
        """Write a tool_executions row (fire-and-forget)."""
        # Coerce output to string in case caller passes a dict/object
        out_str = output_text if isinstance(output_text, str) else json.dumps(output_text)
        await self.insert("tool_executions", {
            "tool_name": tool_name,
            "input": str(input_text)[:2000],
            "output": out_str[:4000],
            "status": status,
            "duration_ms": duration_ms,
            "session_id": self.current_conversation_id,
        })

    async def get_recent_messages(self, conversation_id: Optional[str] = None,
                                   limit: int = 20) -> List[Dict]:
        """Return recent messages, newest first."""
        cid = conversation_id or self.current_conversation_id
        if cid:
            filters = (f"select=role,content,created_at"
                       f"&conversation_id=eq.{cid}"
                       f"&order=created_at.desc&limit={limit}")
        else:
            filters = (f"select=role,content,created_at"
                       f"&order=created_at.desc&limit={limit}")
        return await self.select("messages", filters)

    async def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Return recent conversations with message counts."""
        return await self.select(
            "conversations",
            f"select=id,title,ai_provider,model_name,message_count,created_at"
            f"&order=created_at.desc&limit={limit}",
        )

    async def save_memory_entry(self, key: str, value: Any) -> bool:
        """Upsert a long-term memory entry by key into the agent_memory table."""
        row = await self.upsert("agent_memory", {
            "key": key,
            "value": value if isinstance(value, dict) else {"data": value},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="key")
        return row is not None

    async def load_memory_entries(self) -> Dict:
        """Load all long-term memory entries as {key: value}."""
        rows = await self.select("agent_memory", "select=key,value&order=updated_at.desc")
        result = {}
        for row in rows:
            val = row.get("value") or {}
            result[row["key"]] = val.get("data", val)
        return result


# ------------------------------------------------------------------
# Factory — reads ultron_config.json automatically
# ------------------------------------------------------------------

def create_client_from_config(config_path: str = "ultron_config.json"
                               ) -> Optional["SupabaseClient"]:
    """Create a SupabaseClient from ultron_config.json. Returns None on error."""
    try:
        with open(config_path) as f:
            cfg = json.load(f)
        url = (cfg.get("supabase_url") or "").strip()
        key = (cfg.get("supabase_service_role_key") or
               cfg.get("supabase_anon_key") or "").strip()
        if not url or not key:
            logger.warning("SupabaseClient: supabase_url/key missing in config")
            return None
        return SupabaseClient(url, key)
    except FileNotFoundError:
        logger.warning("SupabaseClient: %s not found", config_path)
        return None
    except Exception as exc:
        logger.warning("SupabaseClient: config load error — %s", exc)
        return None
