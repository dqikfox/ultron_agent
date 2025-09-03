"""
Memory management module for ULTRON Agent 3.0
Handles short-term and long-term memory storage and retrieval
"""
from __future__ import annotations

import json
import logging
import uuid
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..errors import UltronError, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class Memory:
    """Manages short-term and long-term memory storage for the agent."""

    def __init__(
        self,
        short_term_limit: int = 10,
        long_term_file: Union[str, Path] = "long_term_memory.json"
    ) -> None:
        """Initialize memory with specified limits and storage file."""
        self.short_term_limit = short_term_limit
        self.long_term_file = Path(long_term_file)
        
        self.short_term_memory: deque = deque(maxlen=short_term_limit)
        self.long_term_memory: Dict[str, Any] = {}
        
        self._load_long_term_memory()
        logger.info(f"Memory initialized with short-term limit: {short_term_limit}")

    def _load_long_term_memory(self) -> None:
        """Load long-term memory from file."""
        try:
            if self.long_term_file.exists():
                with self.long_term_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.long_term_memory = data
                        logger.info(f"Loaded {len(data)} long-term memories")
                    else:
                        logger.warning("Invalid long-term memory format, starting fresh")
                        self.long_term_memory = {}
            else:
                logger.info("No existing long-term memory file, starting fresh")
                self.long_term_memory = {}
        except Exception as e:
            logger.error(f"Error loading long-term memory: {e}")
            self.long_term_memory = {}

    def save_long_term_memory(self) -> None:
        """Save long-term memory to file."""
        try:
            # Create directory if it doesn't exist
            self.long_term_file.parent.mkdir(parents=True, exist_ok=True)
            
            with self.long_term_file.open('w', encoding='utf-8') as f:
                json.dump(self.long_term_memory, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.long_term_memory)} long-term memories")
        except Exception as e:
            raise UltronError(
                f"Failed to save long-term memory: {e}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.MEDIUM,
                recovery_suggestion="Check file permissions and disk space",
                original_error=e
            )

    def add_to_short_term(self, item: Any) -> None:
        """Add an item to short-term memory."""
        try:
            self.short_term_memory.append(item)
            logger.debug(f"Added to short-term memory: {type(item).__name__}")
        except Exception as e:
            logger.error(f"Error adding to short-term memory: {e}")

    def add_to_long_term(self, item: Any) -> str:
        """Add an item to long-term memory and return the assigned ID."""
        try:
            item_id = str(uuid.uuid4())
            self.long_term_memory[item_id] = item
            
            # Auto-save after adding to long-term memory
            self.save_long_term_memory()
            
            logger.debug(f"Added to long-term memory with ID: {item_id}")
            return item_id
        except Exception as e:
            raise UltronError(
                f"Failed to add to long-term memory: {e}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.MEDIUM,
                original_error=e
            )

    def retrieve_short_term(self) -> List[Any]:
        """Retrieve all short-term memory items."""
        return list(self.short_term_memory)

    def retrieve_long_term(self) -> Dict[str, Any]:
        """Retrieve all long-term memory items."""
        return self.long_term_memory.copy()

    def get_long_term_item(self, item_id: str) -> Optional[Any]:
        """Retrieve a specific long-term memory item by ID."""
        return self.long_term_memory.get(item_id)

    def remove_long_term_item(self, item_id: str) -> bool:
        """Remove a specific long-term memory item by ID."""
        if item_id in self.long_term_memory:
            del self.long_term_memory[item_id]
            self.save_long_term_memory()
            logger.info(f"Removed long-term memory item: {item_id}")
            return True
        return False

    def clear_short_term(self) -> None:
        """Clear all short-term memory."""
        count = len(self.short_term_memory)
        self.short_term_memory.clear()
        logger.info(f"Cleared {count} short-term memory items")

    def clear_long_term(self) -> None:
        """Clear all long-term memory."""
        count = len(self.long_term_memory)
        self.long_term_memory.clear()
        self.save_long_term_memory()
        logger.info(f"Cleared {count} long-term memory items")

    def get_recent_memory(self, limit: int = 5) -> List[Any]:
        """Get recent memory items for agent network queries."""
        recent_items = []
        
        # Get recent short-term memory
        short_term_items = list(self.short_term_memory)
        recent_items.extend(short_term_items[-limit:])
        
        # Get recent long-term memory if needed
        if len(recent_items) < limit:
            long_term_items = list(self.long_term_memory.values())
            remaining = limit - len(recent_items)
            recent_items.extend(long_term_items[-remaining:])
        
        return recent_items[:limit]

    def search_memory(self, query: str) -> List[Any]:
        """Search memory for relevant items."""
        if not query:
            return []
            
        results = []
        query_lower = query.lower()
        
        # Search short-term memory
        for item in self.short_term_memory:
            if self._item_matches_query(item, query_lower):
                results.append(item)
        
        # Search long-term memory
        for item in self.long_term_memory.values():
            if self._item_matches_query(item, query_lower):
                results.append(item)
        
        logger.debug(f"Memory search for '{query}' found {len(results)} results")
        return results

    def _item_matches_query(self, item: Any, query_lower: str) -> bool:
        """Check if an item matches the search query."""
        try:
            if isinstance(item, str):
                return query_lower in item.lower()
            elif isinstance(item, dict):
                return any(
                    query_lower in str(v).lower() 
                    for v in item.values() 
                    if v is not None
                )
            elif hasattr(item, '__str__'):
                return query_lower in str(item).lower()
        except Exception:
            pass  # Ignore errors during search
        return False

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage."""
        return {
            "short_term": {
                "count": len(self.short_term_memory),
                "limit": self.short_term_limit,
                "utilization": len(self.short_term_memory) / self.short_term_limit
            },
            "long_term": {
                "count": len(self.long_term_memory),
                "file_exists": self.long_term_file.exists(),
                "file_size": self.long_term_file.stat().st_size if self.long_term_file.exists() else 0
            }
        }

    def optimize_memory(self) -> None:
        """Optimize memory usage by removing old or duplicate items."""
        # For now, just ensure long-term memory is saved
        # Future: implement deduplication, aging, etc.
        self.save_long_term_memory()
        logger.info("Memory optimization completed")