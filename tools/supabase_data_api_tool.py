"""
Supabase Data API Tool for ULTRON Agent

Full CRUD access to the hosted Supabase PostgREST Data API.
Tables: ai_providers, conversations, messages, agent_memory,
        tool_executions, file_uploads
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from utils.ultron_logger import log_error, log_info

from .tool_interface import ToolInterface

# Canonical table→column map (based on live schema)
TABLE_SCHEMAS: Dict[str, List[str]] = {
    "ai_providers": [
        "id", "user_id", "provider_name", "api_key_encrypted",
        "base_url", "model_list", "is_active", "created_at", "updated_at",
    ],
    "conversations": [
        "id", "user_id", "title", "ai_provider", "model_name",
        "message_count", "created_at", "updated_at",
    ],
    "messages": [
        "id", "conversation_id", "user_id", "role", "content",
        "message_type", "file_url", "processing_time_ms", "tokens_used",
        "created_at",
    ],
    "agent_memory": [
        "id", "key", "value", "memory_type", "created_at", "updated_at",
    ],
    "tool_executions": [
        "id", "tool_name", "input", "output", "status",
        "duration_ms", "session_id", "created_at",
    ],
    "file_uploads": [
        "id", "user_id", "file_url", "processing_result",
        "ocr_text", "ai_analysis", "created_at", "processed_at",
    ],
}

VALID_TABLES = set(TABLE_SCHEMAS.keys())


class SupabaseDataAPITool(ToolInterface):
    """
    Exposes the Supabase PostgREST Data API to ULTRON via natural language
    commands and structured kwargs.

    Supported commands:
      select <table> [filter=...] [limit=N] [order=col.asc/desc]
      insert <table> data=<json>
      update <table> filter=<qs> data=<json>
      delete <table> filter=<qs>
      upsert <table> data=<json> [on_conflict=col]
      schema                     — list all tables and columns
      count <table> [filter=<qs>]
      memory get <key>           — read agent_memory by key
      memory set <key> <value>   — upsert agent_memory
      providers                  — list ai_providers
      recent messages [N]        — last N messages across all conversations
    """

    # Injected by agent_core after SupabaseClient is ready
    _client: ClassVar[Optional[Any]] = None

    @property
    def name(self) -> str:
        return "Supabase Data API"

    @property
    def description(self) -> str:
        return (
            "Full CRUD access to the hosted Supabase database via the PostgREST "
            "Data API. Read/write all tables: ai_providers, conversations, messages, "
            "agent_memory, tool_executions, file_uploads."
        )

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config: Dict[str, Any] = config or {}
        self._base_url: Optional[str] = None
        self._anon_key: Optional[str] = None
        self._svc_key: Optional[str] = None
        self._load_keys()

    def _load_keys(self) -> None:
        """Load connection details from config or ultron_config.json."""
        cfg = self.config
        if not cfg:
            try:
                import os
                cfg_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "ultron_config.json",
                )
                with open(cfg_path) as f:
                    cfg = json.load(f)
            except Exception:
                cfg = {}

        url = (cfg.get("supabase_hosted_url") or cfg.get("supabase_url") or "").strip()
        if url and "localhost" in url:
            # Prefer the hosted URL
            url = cfg.get("supabase_hosted_url", url).strip()
        self._base_url = url.rstrip("/") if url else None
        self._anon_key = (cfg.get("supabase_anon_key") or "").strip() or None
        self._svc_key = (cfg.get("supabase_service_role_key") or "").strip() or None

    # ------------------------------------------------------------------
    # ToolInterface contract
    # ------------------------------------------------------------------

    def match(self, command: str) -> bool:
        kw = [
            "supabase", "data api", "database query", "db query",
            "select from", "insert into", "agent memory",
            "memory set", "memory get", "recent messages",
            "list providers", "tool executions",
        ]
        cmd = command.lower()
        return any(k in cmd for k in kw)

    def execute(self, command: str, **kwargs: Any) -> str:
        """Dispatch command string to the appropriate CRUD operation."""
        if not self._base_url:
            self._load_keys()
        if not self._base_url:
            return "Supabase URL not configured. Set supabase_hosted_url in ultron_config.json."

        cmd = command.lower().strip()

        # --- natural shorthand helpers ---
        if cmd == "schema" or "list tables" in cmd:
            return self._schema_summary()

        if cmd.startswith("providers") or "list providers" in cmd:
            return self._select("ai_providers", "select=provider_name,base_url,model_list,is_active&order=provider_name.asc")

        if "recent messages" in cmd:
            limit = kwargs.get("limit", 20)
            parts = cmd.split()
            for p in parts:
                if p.isdigit():
                    limit = int(p)
                    break
            return self._select("messages",
                                f"select=role,content,created_at&order=created_at.desc&limit={limit}")

        if cmd.startswith("memory get"):
            key = cmd.replace("memory get", "").strip() or kwargs.get("key", "")
            return self._memory_get(key)

        if cmd.startswith("memory set"):
            key = kwargs.get("key", "")
            value = kwargs.get("value", {})
            return self._memory_set(key, value)

        if cmd.startswith("count"):
            parts = cmd.split()
            table = parts[1] if len(parts) > 1 else kwargs.get("table", "")
            filt = kwargs.get("filter", "")
            return self._count(table, filt)

        # --- generic CRUD ---
        for verb in ("select", "insert", "update", "delete", "upsert"):
            if cmd.startswith(verb):
                rest = cmd[len(verb):].strip()
                parts = rest.split(None, 1)
                table = parts[0] if parts else kwargs.get("table", "")
                if verb == "select":
                    filt = kwargs.get("filter", "select=*")
                    limit = kwargs.get("limit", 50)
                    order = kwargs.get("order", "")
                    qs = filt
                    if order and "order=" not in qs:
                        qs += f"&order={order}"
                    if "limit=" not in qs:
                        qs += f"&limit={limit}"
                    return self._select(table, qs)
                if verb == "insert":
                    data = kwargs.get("data") or {}
                    if isinstance(data, str):
                        try:
                            data = json.loads(data)
                        except Exception:
                            return f"data= must be valid JSON, got: {data}"
                    return self._insert(table, data)
                if verb == "update":
                    filt = kwargs.get("filter", "")
                    data = kwargs.get("data") or {}
                    if isinstance(data, str):
                        data = json.loads(data)
                    return self._update(table, filt, data)
                if verb == "delete":
                    filt = kwargs.get("filter", "")
                    return self._delete(table, filt)
                if verb == "upsert":
                    data = kwargs.get("data") or {}
                    if isinstance(data, str):
                        data = json.loads(data)
                    conflict = kwargs.get("on_conflict", "id")
                    return self._upsert(table, data, conflict)

        return (
            "Unknown command. Examples:\n"
            "  select ai_providers\n"
            "  memory get goal_01\n"
            "  memory set goal_01 (pass key= value= as kwargs)\n"
            "  recent messages 10\n"
            "  schema\n"
            "  insert messages (pass data={...} as kwargs)"
        )

    @classmethod
    def schema(cls) -> Dict[str, Any]:
        return {
            "name": "supabase_data_api",
            "description": (
                "Full CRUD on Supabase hosted database. Tables: "
                + ", ".join(sorted(VALID_TABLES))
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "Command string. Examples:\n"
                            "  'select conversations filter=order=created_at.desc limit=5'\n"
                            "  'insert messages' (with data={...} kwarg)\n"
                            "  'memory get my_key'\n"
                            "  'memory set' (with key= value= kwargs)\n"
                            "  'providers'\n"
                            "  'recent messages 10'\n"
                            "  'schema'"
                        ),
                    },
                    "table": {"type": "string", "description": "Table name override"},
                    "filter": {"type": "string", "description": "PostgREST query string"},
                    "data": {"type": "object", "description": "Row data for insert/update"},
                    "limit": {"type": "integer", "description": "Row limit (default 50)"},
                    "key": {"type": "string", "description": "agent_memory key"},
                    "value": {"description": "agent_memory value (any JSON-serialisable)"},
                },
                "required": ["command"],
            },
        }

    def self_test(self) -> Dict[str, Any]:
        """Verify connectivity and do a live read of ai_providers."""
        self._load_keys()
        if not self._base_url:
            return {"status": "error", "message": "supabase_hosted_url not configured"}
        if not self._anon_key:
            return {"status": "error", "message": "supabase_anon_key not configured"}

        result = self._select(
            "ai_providers",
            "select=provider_name,is_active&order=provider_name.asc",
            key=self._anon_key,
        )
        try:
            rows = json.loads(result)
            if isinstance(rows, list):
                names = [r.get("provider_name") for r in rows]
                return {
                    "status": "ok",
                    "message": f"Data API reachable. Providers: {names}",
                    "provider_count": len(rows),
                }
            return {"status": "warning", "message": f"Unexpected response: {result[:200]}"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    # ------------------------------------------------------------------
    # High-level helpers
    # ------------------------------------------------------------------

    def _schema_summary(self) -> str:
        lines = ["Supabase tables and columns:\n"]
        for table, cols in sorted(TABLE_SCHEMAS.items()):
            lines.append(f"  {table}: {', '.join(cols)}")
        return "\n".join(lines)

    def _memory_get(self, key: str) -> str:
        if not key:
            return "memory get requires a key name."
        result = self._select(
            "agent_memory",
            f"select=key,value,memory_type,updated_at&key=eq.{urllib.parse.quote(key)}",
        )
        try:
            rows = json.loads(result)
            if not rows:
                return f"No memory entry found for key '{key}'."
            row = rows[0]
            val = row.get("value", {})
            return json.dumps({"key": row["key"], "value": val,
                               "memory_type": row.get("memory_type"),
                               "updated_at": row.get("updated_at")}, indent=2)
        except Exception:
            return result

    def _memory_set(self, key: str, value: Any) -> str:
        if not key:
            return "memory set requires key= kwarg."
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except Exception:
                value = {"data": value}
        return self._upsert(
            "agent_memory",
            {
                "key": key,
                "value": value,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            on_conflict="key",
        )

    def _count(self, table: str, filters: str = "") -> str:
        if table not in VALID_TABLES:
            return f"Unknown table '{table}'. Valid: {sorted(VALID_TABLES)}"
        qs = filters or ""
        url = f"{self._base_url}/rest/v1/{table}"
        if qs:
            url += f"?{qs}"
        key = self._svc_key or self._anon_key
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Prefer": "count=exact",
            "Range-Unit": "items",
            "Range": "0-0",
        }
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                content_range = resp.getheader("Content-Range", "")
                # "0-0/42" → 42
                total = content_range.split("/")[-1] if "/" in content_range else "?"
                return f"{table}: {total} row(s)"
        except Exception as exc:
            return f"count error: {exc}"

    # ------------------------------------------------------------------
    # Raw HTTP CRUD (sync, stdlib only — no extra deps)
    # ------------------------------------------------------------------

    def _key_for_write(self) -> str:
        return self._svc_key or self._anon_key or ""

    def _select(self, table: str, qs: str = "select=*", key: Optional[str] = None) -> str:
        if table not in VALID_TABLES:
            return f"Unknown table '{table}'. Valid: {sorted(VALID_TABLES)}"
        use_key = key or self._anon_key or self._svc_key or ""
        url = f"{self._base_url}/rest/v1/{table}?{qs}"
        headers = {
            "apikey": use_key,
            "Authorization": f"Bearer {use_key}",
            "Accept": "application/json",
        }
        return self._request("GET", url, headers)

    def _insert(self, table: str, data: Dict) -> str:
        if table not in VALID_TABLES:
            return f"Unknown table '{table}'."
        url = f"{self._base_url}/rest/v1/{table}"
        key = self._key_for_write()
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        return self._request("POST", url, headers, body=json.dumps(data).encode())

    def _update(self, table: str, filters: str, data: Dict) -> str:
        if table not in VALID_TABLES:
            return f"Unknown table '{table}'."
        if not filters:
            return "update requires a filter= to avoid full-table overwrite."
        url = f"{self._base_url}/rest/v1/{table}?{filters}"
        key = self._key_for_write()
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        return self._request("PATCH", url, headers, body=json.dumps(data).encode())

    def _delete(self, table: str, filters: str) -> str:
        if table not in VALID_TABLES:
            return f"Unknown table '{table}'."
        if not filters:
            return "delete requires a filter= to avoid full-table deletion."
        url = f"{self._base_url}/rest/v1/{table}?{filters}"
        key = self._key_for_write()
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Prefer": "return=minimal",
        }
        return self._request("DELETE", url, headers)

    def _upsert(self, table: str, data: Dict, on_conflict: str = "id") -> str:
        if table not in VALID_TABLES:
            return f"Unknown table '{table}'."
        url = f"{self._base_url}/rest/v1/{table}?on_conflict={on_conflict}"
        key = self._key_for_write()
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation,resolution=merge-duplicates",
        }
        return self._request("POST", url, headers, body=json.dumps(data).encode())

    @staticmethod
    def _request(method: str, url: str, headers: Dict,
                  body: Optional[bytes] = None) -> str:
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
                # Pretty-print JSON if possible
                try:
                    parsed = json.loads(raw)
                    return json.dumps(parsed, indent=2)
                except Exception:
                    return raw or "(empty — success)"
        except urllib.error.HTTPError as exc:
            body_err = exc.read().decode("utf-8", errors="replace")
            try:
                err = json.loads(body_err)
                return f"HTTP {exc.code}: {err.get('message', body_err)}"
            except Exception:
                return f"HTTP {exc.code}: {body_err[:500]}"
        except Exception as exc:
            log_error("supabase_data_api", f"Request failed: {exc}")
            return f"Request error: {exc}"

    @classmethod
    def set_client(cls, client: Any) -> None:
        """Optionally inject the shared SupabaseClient (for future async integration)."""
        cls._client = client
