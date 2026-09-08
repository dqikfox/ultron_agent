"""
memory_enhanced.py
===================

Extended memory implementations for the Ultron Agent.  These classes build
upon the basic Memory class provided in the core repository (see
`memory.py`) and add features such as vector embeddings and persistent
storage via external databases.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

try:
    # Optional import for embedding; if unavailable, we will use simple text
    # hashing instead.
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError: # pragma: no cover
    SentenceTransformer = None  # type: ignore
    np = None  # type: ignore

from collections import deque


class VectorMemory:
    """An enhanced memory that stores both raw items and vector embeddings."""

    def __init__(self, short_term_limit: int = 10, model_name: str = 'all-MiniLM-L6-v2') -> None:
        self.short_term_memory: deque[Any] = deque(maxlen=short_term_limit)
        self.long_term_memory: Dict[str, Dict[str, Any]] = {}
        self.model_name = model_name
        if SentenceTransformer:
            try:
                self.embedder = SentenceTransformer(model_name)
                logging.info(f"[VectorMemory] Loaded embedding model: {model_name} - memory_enhanced.py:38")
            except Exception as e:
                logging.error(f"[VectorMemory] Failed to load embedding model: {e} - memory_enhanced.py:40")
                self.embedder = None
        else:
            self.embedder = None

    def _embed(self, text: str) -> List[float]:
        """Compute a vector representation for the given text."""
        if self.embedder:
            try:
                vec = self.embedder.encode([text])[0]
                return vec.tolist()  # type: ignore[no-any-return]
            except Exception as e:
                logging.error(f"[VectorMemory] Embedding error: {e}. Falling back to hashing. - memory_enhanced.py:52")
        # Simple fallback: map characters to floats
        return [float(ord(c)) / 255.0 for c in text][:128]

    def add(self, item: Any) -> None:
        """Add an item to both short-term and long-term memory with embedding."""
        self.short_term_memory.append(item)
        key = str(len(self.long_term_memory) + 1)
        embedding = self._embed(str(item))
        self.long_term_memory[key] = {'item': item, 'embedding': embedding}
        logging.debug(f"[VectorMemory] Added item {key}: {item} - memory_enhanced.py:62")

    def get_recent(self, limit: int = 5) -> List[Any]:
        """Return the most recent items from memory."""
        return list(self.short_term_memory)[-limit:]

    def search(self, query: str, top_k: int = 3) -> List[Any]:
        """Return up to `top_k` items whose embeddings are closest to the query."""
        if not self.long_term_memory:
            return []
        query_vec = self._embed(query)
        scored: List[tuple[float, Dict[str, Any]]] = []
        for info in self.long_term_memory.values():
            item_vec = info['embedding']
            if np is not None and len(query_vec) == len(item_vec):
                try:
                    sim = float(np.dot(query_vec, item_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(item_vec) + 1e-8))
                except Exception as e:
                    logging.error(f"[VectorMemory] Similarity error: {e} - memory_enhanced.py:80")
                    sim = 0.0
            else:
                sim = len(set(str(info['item'])) & set(query)) / max(len(set(query)), 1)
            scored.append((sim, info))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [info['item'] for sim, info in scored[:top_k]]
