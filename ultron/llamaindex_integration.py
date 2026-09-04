"""
LlamaIndex Integration for ULTRON Agent
Provides unified LLM access, RAG pipelines, and agent workflows
via LlamaIndex framework (https://docs.llamaindex.ai)
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)


class LlamaIndexBridge:
    """
    Central bridge between ULTRON and the LlamaIndex framework.

    Responsibilities:
    - Build provider-aware LLM instances (Ollama / OpenAI / Anthropic)
    - Create a RAG VectorStoreIndex over the agent's long-term memory
    - Expose a query engine and a chat engine for downstream use
    - Expose the raw llama_index Settings object for advanced callers
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self._llm = None
        self._embed_model = None
        self._index = None
        self._query_engine = None
        self._chat_engine = None
        self._initialized = False

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def initialize(self) -> bool:
        """
        Initialise LlamaIndex Settings and build the RAG index.
        Failures at individual steps are isolated — the bridge still becomes
        ready as long as embeddings + index succeed.
        Returns True on success.
        """
        try:
            from llama_index.core import Settings, VectorStoreIndex
            from llama_index.core.node_parser import SentenceSplitter

            # --- Embedding model (required for RAG) ---
            self._embed_model = self._build_embed_model()
            Settings.embed_model = self._embed_model
            Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=64)

            # --- LLM (optional — index still works without it for pure RAG) ---
            try:
                self._llm = self._build_llm()
                Settings.llm = self._llm
                logger.info("LlamaIndex: LLM ready (%s)", type(self._llm).__name__)
            except Exception as llm_err:
                logger.warning(
                    "LlamaIndex: LLM init failed (%s) — RAG index will work but "
                    "chat/complete disabled until LLM is available.",
                    llm_err,
                )
                self._llm = None
                # Tell LlamaIndex not to use any LLM during index builds
                try:
                    from llama_index.core.llms import MockLLM
                    Settings.llm = MockLLM()
                except Exception:
                    pass

            # --- Memory index ---
            docs = self._load_memory_documents()
            # Build index using embed model only (no LLM calls during ingestion)
            self._index = VectorStoreIndex.from_documents(
                docs,
                show_progress=False,
            )
            self._query_engine = self._index.as_query_engine(similarity_top_k=5)
            self._chat_engine = self._index.as_chat_engine(
                chat_mode="condense_plus_context",
                similarity_top_k=5,
            )
            logger.info(
                "LlamaIndex: indexed %d memory document(s). Embed=%s.",
                len(docs),
                type(self._embed_model).__name__,
            )

            self._initialized = True
            logger.info(
                "LlamaIndex: bridge ready. Provider=%s, Embed=%s",
                self.config.get("llm_provider", "ollama"),
                type(self._embed_model).__name__,
            )
            return True

        except Exception as exc:
            logger.warning("LlamaIndex: initialisation failed — %s", exc)
            return False

    # ------------------------------------------------------------------
    # LLM factory
    # ------------------------------------------------------------------

    def _build_llm(self):
        """Return the best available LLM based on config."""
        provider = self.config.get("llm_provider", "ollama").lower()

        if provider == "openai":
            return self._build_openai_llm()
        if provider == "anthropic":
            return self._build_anthropic_llm()
        # Default: Ollama
        return self._build_ollama_llm()

    def _build_ollama_llm(self):
        from llama_index.llms.ollama import Ollama

        model = self.config.get("llm_model", "llama3")
        base_url = self.config.get("ollama_base_url", "http://localhost:11434")
        return Ollama(model=model, base_url=base_url, request_timeout=120.0)

    def _build_openai_llm(self):
        from llama_index.llms.openai import OpenAI

        api_key = self.config.get("openai_api_key", "")
        model = self.config.get("openai_model", "gpt-4o-mini")
        return OpenAI(model=model, api_key=api_key or None)

    def _build_anthropic_llm(self):
        from llama_index.llms.anthropic import Anthropic

        api_key = self.config.get("anthropic_api_key", "")
        model = self.config.get("anthropic_model", "claude-3-5-sonnet-20241022")
        return Anthropic(model=model, api_key=api_key or None)

    # ------------------------------------------------------------------
    # Embedding factory
    # ------------------------------------------------------------------

    def _build_embed_model(self):
        """Return the best available embedding model, preferring local options."""
        # 1. Ollama nomic-embed-text — fast, local, no download needed
        try:
            from llama_index.embeddings.ollama import OllamaEmbedding
            base_url = self.config.get("ollama_base_url", "http://localhost:11434")
            return OllamaEmbedding(
                model_name="nomic-embed-text",
                base_url=base_url,
            )
        except Exception:
            pass

        # 2. OpenAI text-embedding-3-small — if API key present
        openai_key = self.config.get("openai_api_key", "")
        if openai_key:
            try:
                from llama_index.embeddings.openai import OpenAIEmbedding
                return OpenAIEmbedding(api_key=openai_key)
            except Exception:
                pass

        # 3. Local HuggingFace BAAI/bge-small — always works, downloads on first use
        try:
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            return HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        except Exception:
            pass

        # 4. LlamaIndex default resolver as last resort
        from llama_index.core.embeddings import resolve_embed_model
        return resolve_embed_model("default")

    # ------------------------------------------------------------------
    # Memory document loader
    # ------------------------------------------------------------------

    def _load_memory_documents(self) -> List:
        """Load ULTRON's long-term memory JSON as LlamaIndex Documents."""
        from llama_index.core import Document

        docs: List[Document] = []
        memory_file = Path(
            self.config.get("memory_long_term_file", "long_term_memory.json")
        )

        if memory_file.exists():
            try:
                raw = json.loads(memory_file.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    for key, value in raw.items():
                        text = (
                            json.dumps(value, ensure_ascii=False)
                            if not isinstance(value, str)
                            else value
                        )
                        docs.append(Document(text=text, metadata={"memory_key": key}))
                elif isinstance(raw, list):
                    for i, item in enumerate(raw):
                        text = (
                            json.dumps(item, ensure_ascii=False)
                            if not isinstance(item, str)
                            else item
                        )
                        docs.append(Document(text=text, metadata={"index": i}))
                logger.info("Loaded %d documents from long_term_memory.json", len(docs))
            except Exception as exc:
                logger.warning("Could not parse long_term_memory.json: %s", exc)

        # Also try the ultron_memory.json file
        alt_file = Path("ultron_memory.json")
        if alt_file.exists():
            try:
                raw = json.loads(alt_file.read_text(encoding="utf-8"))
                text = json.dumps(raw, ensure_ascii=False, indent=2)
                docs.append(Document(text=text, metadata={"source": "ultron_memory.json"}))
            except Exception:
                pass

        return docs

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def ready(self) -> bool:
        return self._initialized

    @property
    def llm(self):
        """The active LlamaIndex LLM instance."""
        return self._llm

    @property
    def embed_model(self):
        """The active embedding model."""
        return self._embed_model

    @property
    def index(self):
        """The VectorStoreIndex built from agent memory."""
        return self._index

    def query(self, question: str) -> str:
        """
        Run a RAG query against agent memory.
        Returns the synthesised answer string.
        """
        if not self._initialized or self._query_engine is None:
            return "LlamaIndex not initialised."
        try:
            response = self._query_engine.query(question)
            return str(response)
        except Exception as exc:
            logger.error("LlamaIndex query error: %s", exc)
            return f"Query error: {exc}"

    def chat(self, message: str) -> str:
        """
        Stateful chat with memory context via the chat engine.
        """
        if not self._initialized or self._chat_engine is None:
            return "LlamaIndex not initialised."
        try:
            response = self._chat_engine.chat(message)
            return str(response)
        except Exception as exc:
            logger.error("LlamaIndex chat error: %s", exc)
            return f"Chat error: {exc}"

    def llm_complete(self, prompt: str) -> str:
        """Direct completion via the configured LLM (no RAG)."""
        if self._llm is None:
            return "LlamaIndex LLM not initialised."
        try:
            response = self._llm.complete(prompt)
            return str(response)
        except Exception as exc:
            logger.error("LlamaIndex complete error: %s", exc)
            return f"Complete error: {exc}"

    def add_documents(self, texts: List[str], metadata: Optional[List[Dict]] = None) -> int:
        """
        Dynamically add new documents to the in-memory index.
        Returns number of documents added.
        """
        if not self._initialized or self._index is None:
            return 0
        from llama_index.core import Document

        meta_list = metadata or [{}] * len(texts)
        docs = [
            Document(text=t, metadata=m)
            for t, m in zip(texts, meta_list)
        ]
        for doc in docs:
            self._index.insert(doc)

        # Rebuild engines after inserting
        self._query_engine = self._index.as_query_engine(similarity_top_k=5)
        self._chat_engine = self._index.as_chat_engine(
            chat_mode="condense_plus_context", similarity_top_k=5
        )
        return len(docs)

    def get_available_providers(self) -> Dict[str, bool]:
        """Return which LLM providers are configured and available."""
        return {
            "ollama": bool(self.config.get("ollama_base_url") or True),
            "openai": bool(self.config.get("openai_api_key")),
            "anthropic": bool(self.config.get("anthropic_api_key")),
        }

    def switch_provider(self, provider: str) -> str:
        """Dynamically switch the active LLM provider."""
        from llama_index.core import Settings

        original = self.config.get("llm_provider", "ollama")
        self.config["llm_provider"] = provider.lower()
        try:
            self._llm = self._build_llm()
            Settings.llm = self._llm
            return f"Switched LLM provider from '{original}' to '{provider}'."
        except Exception as exc:
            self.config["llm_provider"] = original
            return f"Failed to switch to '{provider}': {exc}"

    def status(self) -> Dict[str, Any]:
        """Return current bridge status."""
        return {
            "initialized": self._initialized,
            "llm_provider": self.config.get("llm_provider", "ollama"),
            "llm_model": self.config.get("llm_model", "unknown"),
            "embed_model": type(self._embed_model).__name__ if self._embed_model else None,
            "index_node_count": (
                len(self._index.docstore.docs) if self._index and hasattr(self._index, "docstore") else 0
            ),
            "providers_available": self.get_available_providers(),
        }


# Module-level singleton — initialised once by agent_core
_bridge_instance: Optional[LlamaIndexBridge] = None


def get_bridge() -> Optional[LlamaIndexBridge]:
    """Return the module-level bridge singleton (None if not yet initialised)."""
    return _bridge_instance


def init_bridge(config: Dict[str, Any]) -> LlamaIndexBridge:
    """Initialise (or return existing) bridge singleton."""
    global _bridge_instance
    if _bridge_instance is None or not _bridge_instance.ready:
        _bridge_instance = LlamaIndexBridge(config)
        _bridge_instance.initialize()
    return _bridge_instance
