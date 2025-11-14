import logging
from collections import OrderedDict
import threading
from typing import Any, Dict

# Set up logger
ultron_logger = logging.getLogger('IntelligentCache')
ultron_logger.setLevel(logging.DEBUG)

class IntelligentCache:
    def __init__(self, cache_size: int):
        self.cache_size = cache_size
        self.items = OrderedDict()
        self.importances = {}
        self.lock = threading.Lock()

    def _update_importance(self, item_id, importance):
        with self.lock:
            self.importances[item_id] = importance

    def get(self, key: str) -> Any:
        # Check if the item is in the cache
        if key in self.items:
            # Update the item's importance (example: decay)
            self._update_importance(key, 0.9 * self.importances[key])
            return self.items.pop(key), True  # Cache hit
        else:
            return None, False  # Cache miss

    def set(self, key: str, value: Any):
        with self.lock:
            if len(self.items) >= self.cache_size:
                oldest_key = next(iter(self.items))
                del self.items[oldest_key]
                del self.importances[oldest_key]
            self.items[key] = value
            self._update_importance(key, 1.0)  # Cache hit

    def invalidate(self):
        with self.lock:
            for key in list(self.items.keys()):
                if key not in self.importances or self.importances[key] < 0.5:
                    del self.items[key]
                    del self.importances[key]

    def warm_cache(self, item_ids: Dict[str, Any]):
        with self.lock:
            for item_id, _ in item_ids.items():
                if item_id not in self.items:
                    self.set(item_id, None)  # Mark as warm item

    def get_stats(self) -> Dict[str, float]:
        return {
            'hit_rate': sum(1 for item_id, _ in self.importances.values() if self.importances[item_id] > 0.5) / len(self.items),
            'miss_rate': 1 - sum(1 for item_id, _ in self.importances.values() if self.importances[item_id] > 0.5) / len(self.items)
        }