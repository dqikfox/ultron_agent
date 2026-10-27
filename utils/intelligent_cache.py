import logging
import time
from collections import OrderedDict
import threading
from typing import Any, Dict, List, Optional, Tuple

# Set up logger
ultron_logger = logging.getLogger('IntelligentCache')
ultron_logger.setLevel(logging.DEBUG)


class IntelligentCache:
    """
    LRU cache with importance-weighted eviction, optional TTL, and
    accurate hit/miss statistics.

    Changes vs. original:
    - Fixed ``get_stats()`` crash (floats are not iterable as pairs).
    - Fixed ``get()`` not re-inserting the item after it was popped
      (move-to-end preserves recency without data loss).
    - Added per-key TTL support via ``ttl_seconds`` constructor arg.
    - Added dedicated ``_hit_count`` / ``_miss_count`` counters so
      ``get_stats()`` reports accurate rates across the lifetime of the
      cache, not just the current snapshot.
    - Added ``batch_get`` / ``batch_set`` for bulk operations.
    - Added ``delete`` to remove a single key.
    """

    def __init__(self, cache_size: int, ttl_seconds: Optional[float] = None):
        self.cache_size = cache_size
        self.ttl_seconds = ttl_seconds
        self.items: OrderedDict[str, Any] = OrderedDict()
        self.importances: Dict[str, float] = {}
        self._expires_at: Dict[str, Optional[float]] = {}
        self._hit_count: int = 0
        self._miss_count: int = 0
        self.lock = threading.Lock()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _update_importance(self, item_id: str, importance: float) -> None:
        self.importances[item_id] = importance

    def _is_expired(self, key: str) -> bool:
        """Return True when key has a TTL that has elapsed."""
        exp = self._expires_at.get(key)
        return exp is not None and time.monotonic() > exp

    def _evict_expired(self) -> None:
        """Remove all keys whose TTL has elapsed (call while holding lock)."""
        expired = [k for k in list(self.items.keys()) if self._is_expired(k)]
        for k in expired:
            del self.items[k]
            self.importances.pop(k, None)
            self._expires_at.pop(k, None)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str) -> Tuple[Any, bool]:
        """Return ``(value, True)`` on hit, ``(None, False)`` on miss."""
        with self.lock:
            self._evict_expired()
            if key in self.items:
                if self._is_expired(key):
                    # Expired during this call
                    del self.items[key]
                    self.importances.pop(key, None)
                    self._expires_at.pop(key, None)
                    self._miss_count += 1
                    return None, False
                # Decay importance slightly and move to MRU position
                self._update_importance(key, max(0.0, self.importances.get(key, 1.0) * 0.9))
                self.items.move_to_end(key)
                self._hit_count += 1
                return self.items[key], True
            self._miss_count += 1
            return None, False

    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        """Insert or update a cache entry with an optional per-key TTL."""
        with self.lock:
            self._evict_expired()
            if key in self.items:
                self.items.move_to_end(key)
            elif len(self.items) >= self.cache_size:
                # Evict the least-important item (lowest importance score)
                if self.importances:
                    lru_key = min(self.importances, key=lambda k: self.importances[k])
                else:
                    lru_key = next(iter(self.items))
                del self.items[lru_key]
                self.importances.pop(lru_key, None)
                self._expires_at.pop(lru_key, None)
            self.items[key] = value
            self._update_importance(key, 1.0)
            effective_ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds
            self._expires_at[key] = (
                time.monotonic() + effective_ttl if effective_ttl is not None else None
            )

    def delete(self, key: str) -> bool:
        """Remove a single key. Returns True if the key existed."""
        with self.lock:
            if key in self.items:
                del self.items[key]
                self.importances.pop(key, None)
                self._expires_at.pop(key, None)
                return True
            return False

    def invalidate(self) -> None:
        """Remove entries whose importance has decayed below 0.5, plus expired ones."""
        with self.lock:
            self._evict_expired()
            to_remove = [k for k, imp in list(self.importances.items()) if imp < 0.5]
            for k in to_remove:
                self.items.pop(k, None)
                del self.importances[k]
                self._expires_at.pop(k, None)

    def warm_cache(self, item_ids: Dict[str, Any]) -> None:
        """Pre-populate entries without evicting existing live data."""
        for item_id, value in item_ids.items():
            if item_id not in self.items:
                self.set(item_id, value)

    def batch_get(self, keys: List[str]) -> Dict[str, Any]:
        """Fetch multiple keys at once. Missing/expired keys are omitted."""
        result: Dict[str, Any] = {}
        for key in keys:
            value, hit = self.get(key)
            if hit:
                result[key] = value
        return result

    def batch_set(self, items: Dict[str, Any],
                  ttl_seconds: Optional[float] = None) -> None:
        """Insert multiple key-value pairs in one call."""
        for key, value in items.items():
            self.set(key, value, ttl_seconds=ttl_seconds)

    def get_stats(self) -> Dict[str, Any]:
        """Return cache statistics including accurate hit/miss rates."""
        with self.lock:
            self._evict_expired()
            total = self._hit_count + self._miss_count
            hit_rate = self._hit_count / total if total > 0 else 0.0
            miss_rate = self._miss_count / total if total > 0 else 0.0
            high_importance = sum(
                1 for imp in self.importances.values() if imp >= 0.5
            )
            return {
                "size": len(self.items),
                "capacity": self.cache_size,
                "hit_count": self._hit_count,
                "miss_count": self._miss_count,
                "hit_rate": round(hit_rate, 4),
                "miss_rate": round(miss_rate, 4),
                "high_importance_entries": high_importance,
                "ttl_enabled": self.ttl_seconds is not None,
            }