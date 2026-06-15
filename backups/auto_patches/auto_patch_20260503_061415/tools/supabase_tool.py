"""
Supabase tool — lets ULTRON query its own conversation history,
recall past messages, and inspect persisted memory via natural language.
"""

import re
from typing import Any, Dict

from tools.tool_interface import ToolInterface

RECALL_PATTERNS = re.compile(
    r"\b(recall|history|past session|previous|what did (i|you|we) (do|say|talk)|"
    r"remember|last time|earlier|show.*conversation|show.*messages|search.*memory)\b",
    re.IGNORECASE,
)


class SupabaseTool(ToolInterface):
    """Query ULTRON's Supabase-backed conversation history and memory."""

    name = "supabase_tool"
    description = (
        "Query ULTRON's conversation history, recalled messages, and "
        "persisted long-term memory stored in Supabase."
    )

    def match(self, command: str, context: Dict = None) -> bool:
        return bool(RECALL_PATTERNS.search(command))

    async def execute(self, command: str, context: Dict = None) -> Dict[str, Any]:
        client = getattr(self.__class__, "shared_supabase", None)

        if not client or not client.available:
            return {
                "status": "unavailable",
                "response": (
                    "Supabase is not connected. Start the local stack with "
                    "`npx supabase start` to enable conversation history."
                ),
            }

        cmd_lower = command.lower()

        # ── Memory recall ─────────────────────────────────────────────────
        if any(w in cmd_lower for w in ("remember", "memory", "recall")):
            entries = await client.load_memory_entries()
            if not entries:
                return {"status": "ok", "response": "No long-term memory entries found."}
            lines = [f"• **{k}**: {v}" for k, v in list(entries.items())[:20]]
            return {
                "status": "ok",
                "response": "Long-term memory:\n" + "\n".join(lines),
                "data": entries,
            }

        # ── Conversation listing ───────────────────────────────────────────
        if any(w in cmd_lower for w in ("history", "conversation", "past session", "last time")):
            conversations = await client.get_conversation_history(limit=10)
            if not conversations:
                return {"status": "ok", "response": "No past conversations found."}
            lines = []
            for c in conversations:
                ts = (c.get("created_at") or "")[:16]
                lines.append(
                    f"• [{ts}] **{c['title']}** — "
                    f"{c.get('message_count', 0)} messages "
                    f"({c.get('model_name', 'unknown')})"
                )
            return {
                "status": "ok",
                "response": "Past conversations:\n" + "\n".join(lines),
                "data": conversations,
            }

        # ── Recent messages ────────────────────────────────────────────────
        messages = await client.get_recent_messages(limit=10)
        if not messages:
            return {"status": "ok", "response": "No recent messages found."}
        lines = []
        for m in reversed(messages):
            ts = (m.get("created_at") or "")[:16]
            role_label = "🧑 You" if m["role"] == "user" else "🤖 ULTRON"
            lines.append(f"[{ts}] {role_label}: {m['content'][:120]}")
        return {
            "status": "ok",
            "response": "Recent messages:\n" + "\n".join(lines),
            "data": messages,
        }

    def schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "Natural language query about history or memory. "
                            "E.g. 'show recent messages', 'recall memory', "
                            "'show past conversations'."
                        ),
                    }
                },
                "required": ["command"],
            },
        }
