"""
LlamaIndex Tool for ULTRON Agent
Exposes LlamaIndex LLM, RAG, and document indexing capabilities
through the standard ToolInterface.
"""

import json
from typing import Any, ClassVar, Dict, List, Optional

from utils.ultron_logger import log_error, log_info

from .tool_interface import ToolInterface


class LlamaIndexTool(ToolInterface):
    """
    Provides ULTRON with access to the full LlamaIndex framework:
    - Unified LLM chat / completion (Ollama, OpenAI, Anthropic)
    - RAG queries over agent memory
    - Dynamic document ingestion
    - Provider switching at runtime
    """

    # Shared bridge instance wired in by agent_core at startup
    _bridge: ClassVar[Optional[Any]] = None

    @property
    def name(self) -> str:
        return "LlamaIndex"

    @property
    def description(self) -> str:
        return (
            "Access LlamaIndex LLM abstraction, RAG memory queries, "
            "document indexing, and provider switching."
        )

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config: Dict[str, Any] = config or {}

    # ------------------------------------------------------------------
    # ToolInterface contract
    # ------------------------------------------------------------------

    def match(self, command: str) -> bool:
        keywords = [
            "llamaindex", "llama index", "llama-index",
            "rag query", "rag search", "index document",
            "switch llm", "switch provider", "llama chat",
            "memory query", "semantic search",
        ]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs: Any) -> str:
        """Dispatch to sub-command based on keyword matching."""
        bridge = self._get_bridge()
        if bridge is None:
            return "LlamaIndex is not initialised. Call `initialize llamaindex` first."

        cmd = command.lower().strip()

        if "status" in cmd or "info" in cmd:
            return json.dumps(bridge.status(), indent=2)

        if any(kw in cmd for kw in ("rag query", "query memory", "memory query", "semantic search")):
            question = kwargs.get("question") or command
            # Strip command prefix to get the actual question
            for prefix in ("rag query", "query memory", "memory query", "semantic search"):
                if question.lower().startswith(prefix):
                    question = question[len(prefix):].strip(": ").strip()
                    break
            return bridge.query(question)

        if any(kw in cmd for kw in ("llama chat", "chat with memory")):
            message = kwargs.get("message") or command
            return bridge.chat(message)

        if any(kw in cmd for kw in ("complete", "llm complete", "completion")):
            prompt = kwargs.get("prompt") or command
            return bridge.llm_complete(prompt)

        if any(kw in cmd for kw in ("switch provider", "switch llm", "use provider")):
            # Extract provider name from command: "switch provider openai"
            parts = cmd.split()
            provider = parts[-1] if len(parts) > 1 else "ollama"
            return bridge.switch_provider(provider)

        if any(kw in cmd for kw in ("index document", "add document", "ingest")):
            text = kwargs.get("text") or command
            metadata = kwargs.get("metadata")
            count = bridge.add_documents(
                [text],
                [metadata] if metadata else None,
            )
            return f"Added {count} document(s) to the LlamaIndex memory index."

        if "providers" in cmd or "available" in cmd:
            return json.dumps(bridge.get_available_providers(), indent=2)

        # Default: treat the whole command as a chat message
        return bridge.chat(command)

    @classmethod
    def schema(cls) -> Dict[str, Any]:
        return {
            "name": "llamaindex",
            "description": (
                "LlamaIndex integration: RAG queries, LLM chat/completion, "
                "document indexing, and provider switching."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "Command to execute. Examples:\n"
                            "  'rag query: what did the agent decide about architecture?'\n"
                            "  'llama chat: summarise recent agent activity'\n"
                            "  'switch provider openai'\n"
                            "  'index document' (pass text= in kwargs)\n"
                            "  'status'"
                        ),
                    }
                },
                "required": ["command"],
            },
        }

    def self_test(self) -> Dict[str, Any]:
        """Verify LlamaIndex packages are importable and bridge is reachable."""
        errors: List[str] = []

        # Package availability checks
        for pkg in (
            "llama_index.core",
            "llama_index.llms.ollama",
            "llama_index.llms.openai",
            "llama_index.llms.anthropic",
        ):
            try:
                __import__(pkg)
            except ImportError as exc:
                errors.append(f"Missing package '{pkg}': {exc}")

        # Bridge check
        bridge = self._get_bridge()
        if bridge is None:
            errors.append("Bridge singleton not initialised (run init_bridge first).")
        elif not bridge.ready:
            errors.append("Bridge exists but is not ready.")

        if errors:
            return {"status": "warning", "message": "; ".join(errors), "errors": errors}

        status = bridge.status()
        return {
            "status": "ok",
            "message": (
                f"LlamaIndex ready. Provider={status['llm_provider']}, "
                f"Model={status['llm_model']}"
            ),
            "bridge_status": status,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_bridge(self):
        """Return bridge, trying class var first, then module singleton."""
        if LlamaIndexTool._bridge is not None:
            return LlamaIndexTool._bridge
        try:
            from ultron.llamaindex_integration import get_bridge
            return get_bridge()
        except Exception:
            return None

    @classmethod
    def set_bridge(cls, bridge: Any) -> None:
        """Called by agent_core to inject the shared bridge after init."""
        cls._bridge = bridge
        log_info("llamaindex_tool", "Bridge injected into LlamaIndexTool.")
