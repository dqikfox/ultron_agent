"""
Cache Manager for ULTRON Agent 3.0
Implements intelligent multi-level caching with automatic invalidation
"""

import asyncio
import json
import hashlib
import pickle
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, asdict
from collections import OrderedDict
import logging
from security_utils import sanitize_log_input

logger = logging.getLogger(__name__)


@dataclass
class CacheItem:
    """Cache item with metadata."""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    size_bytes: int = 0
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def is_expired(self) -> bool:
        """Check if item has expired."""
        return self.expires_at is not None and datetime.now() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'access_count': self.access_count,
            'size_bytes': self.size_bytes,
            'tags': self.tags
        }


@dataclass
class CacheStatistics:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size: int = 0
    item_count: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0


class MemoryCache:
    """High-speed in-memory cache with LRU eviction."""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheItem] = OrderedDict()
        self.stats = CacheStatistics()
        self._lock = asyncio.Lock()
        
    async def get(self, key: str) -> Optional[CacheItem]:
        """Get item from memory cache."""
        async with self._lock:
            if key in self.cache:
                item = self.cache[key]
                if item.is_expired():
                    del self.cache[key]
                    self.stats.misses += 1
                    return None
                
                # Move to end (LRU)
                self.cache.move_to_end(key)
                item.access_count += 1
                self.stats.hits += 1
                return item
            
            self.stats.misses += 1
            return None
    
    async def set(self, key: str, item: CacheItem) -> bool:
        """Set item in memory cache."""
        async with self._lock:
            try:
                # Calculate item size
                item.size_bytes = len(pickle.dumps(item.value))
                
                # Remove if already exists
                if key in self.cache:
                    old_item = self.cache[key]
                    self.stats.total_size -= old_item.size_bytes
                    del self.cache[key]
                
                # Check memory limit
                if self.stats.total_size + item.size_bytes > self.max_memory_bytes:
                    await self._evict_lru()
                
                # Check size limit
                while len(self.cache) >= self.max_size:
                    await self._evict_lru()
                
                self.cache[key] = item
                self.stats.total_size += item.size_bytes
                self.stats.item_count = len(self.cache)
                return True
                
            except Exception as e:
                logger.error(f"Memory cache set error: {sanitize_log_input(str(e))}")
                return False
    
    async def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if self.cache:
            key, item = self.cache.popitem(last=False)
            self.stats.total_size -= item.size_bytes
            self.stats.evictions += 1
    
    async def invalidate(self, key: str) -> bool:
        """Remove item from cache."""
        async with self._lock:
            if key in self.cache:
                item = self.cache[key]
                del self.cache[key]
                self.stats.total_size -= item.size_bytes
                self.stats.item_count = len(self.cache)
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cached items."""
        async with self._lock:
            self.cache.clear()
            self.stats = CacheStatistics()


class DiskCache:
    """Persistent disk-based cache with compression."""
    
    def __init__(self, cache_dir: str = "cache", max_size_mb: int = 1000):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.stats = CacheStatistics()
        self._lock = asyncio.Lock()
        
    def _get_file_path(self, key: str) -> Path:
        """Get file path for cache key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    async def get(self, key: str) -> Optional[CacheItem]:
        """Get item from disk cache."""
        async with self._lock:
            try:
                file_path = self._get_file_path(key)
                if not file_path.exists():
                    self.stats.misses += 1
                    return None
                
                # Read compressed data
                with gzip.open(file_path, 'rb') as f:
                    data = pickle.load(f)
                
                item = CacheItem(
                    key=data['key'],
                    value=data['value'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    expires_at=datetime.fromisoformat(data['expires_at']) if data['expires_at'] else None,
                    access_count=data['access_count'],
                    size_bytes=data['size_bytes'],
                    tags=data['tags']
                )
                
                if item.is_expired():
                    file_path.unlink(missing_ok=True)
                    self.stats.misses += 1
                    return None
                
                item.access_count += 1
                self.stats.hits += 1
                
                # Update access count on disk
                await self.set(key, item)
                
                return item
                
            except Exception as e:
                logger.error(f"Disk cache get error: {sanitize_log_input(str(e))}")
                self.stats.misses += 1
                return None
    
    async def set(self, key: str, item: CacheItem) -> bool:
        """Set item in disk cache."""
        async with self._lock:
            try:
                file_path = self._get_file_path(key)
                
                # Serialize and compress
                data = item.to_dict()
                with gzip.open(file_path, 'wb') as f:
                    pickle.dump(data, f)
                
                item.size_bytes = file_path.stat().st_size
                self.stats.total_size += item.size_bytes
                
                # Check size limits
                await self._cleanup_old_files()
                
                return True
                
            except Exception as e:
                logger.error(f"Disk cache set error: {sanitize_log_input(str(e))}")
                return False
    
    async def _cleanup_old_files(self) -> None:
        """Remove old files if over size limit."""
        try:
            files = list(self.cache_dir.glob("*.cache"))
            total_size = sum(f.stat().st_size for f in files)
            
            if total_size > self.max_size_bytes:
                # Sort by modification time (oldest first)
                files.sort(key=lambda x: x.stat().st_mtime)
                
                for file_path in files:
                    if total_size <= self.max_size_bytes * 0.8:  # 80% threshold
                        break
                    
                    file_size = file_path.stat().st_size
                    file_path.unlink(missing_ok=True)
                    total_size -= file_size
                    self.stats.evictions += 1
                    
        except Exception as e:
            logger.error(f"Disk cache cleanup error: {sanitize_log_input(str(e))}")


class CacheManager:
    """Multi-level intelligent caching system."""
    
    def __init__(self, 
                 memory_cache_size: int = 1000,
                 memory_cache_mb: int = 100,
                 disk_cache_mb: int = 1000,
                 cache_dir: str = "cache"):
        
        self.memory_cache = MemoryCache(memory_cache_size, memory_cache_mb)
        self.disk_cache = DiskCache(cache_dir, disk_cache_mb)
        self.warming_tasks: Dict[str, asyncio.Task] = {}
        
    async def get(self, key: str, cache_level: str = "auto") -> Optional[Any]:
        """Get value from cache with automatic level selection."""
        try:
            if cache_level in ("auto", "memory"):
                # Try memory cache first
                item = await self.memory_cache.get(key)
                if item:
                    return item.value
            
            if cache_level in ("auto", "disk"):
                # Try disk cache
                item = await self.disk_cache.get(key)
                if item:
                    # Promote to memory cache
                    await self.memory_cache.set(key, item)
                    return item.value
            
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {sanitize_log_input(str(e))}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None) -> bool:
        """Set value in cache with TTL."""
        try:
            expires_at = datetime.now() + timedelta(seconds=ttl) if ttl else None
            
            item = CacheItem(
                key=key,
                value=value,
                created_at=datetime.now(),
                expires_at=expires_at,
                tags=tags or []
            )
            
            # Set in both caches
            memory_ok = await self.memory_cache.set(key, item)
            disk_ok = await self.disk_cache.set(key, item)
            
            return memory_ok or disk_ok
            
        except Exception as e:
            logger.error(f"Cache set error: {sanitize_log_input(str(e))}")
            return False
    
    async def invalidate(self, key_pattern: str) -> int:
        """Invalidate cache entries matching pattern."""
        invalidated = 0
        
        try:
            # Simple pattern matching (could be enhanced with regex)
            if '*' in key_pattern:
                prefix = key_pattern.replace('*', '')
                
                # Invalidate from memory cache
                memory_keys = list(self.memory_cache.cache.keys())
                for key in memory_keys:
                    if key.startswith(prefix):
                        await self.memory_cache.invalidate(key)
                        invalidated += 1
                
                # Invalidate from disk cache  
                for cache_file in self.disk_cache.cache_dir.glob("*.cache"):
                    try:
                        cache_file.unlink()
                        invalidated += 1
                    except:
                        pass
            else:
                # Exact key match
                memory_ok = await self.memory_cache.invalidate(key_pattern)
                disk_file = self.disk_cache._get_file_path(key_pattern)
                disk_ok = disk_file.exists()
                if disk_ok:
                    disk_file.unlink(missing_ok=True)
                
                invalidated = int(memory_ok) + int(disk_ok)
            
            return invalidated
            
        except Exception as e:
            logger.error(f"Cache invalidation error: {sanitize_log_input(str(e))}")
            return 0
    
    async def warm_cache(self, keys: List[str], loader: Callable[[str], Any]) -> None:
        """Pre-warm cache with specified keys."""
        try:
            for key in keys:
                if key not in self.warming_tasks:
                    self.warming_tasks[key] = asyncio.create_task(self._warm_single_key(key, loader))
            
            # Wait for all warming tasks
            await asyncio.gather(*self.warming_tasks.values(), return_exceptions=True)
            self.warming_tasks.clear()
            
        except Exception as e:
            logger.error(f"Cache warming error: {sanitize_log_input(str(e))}")
    
    async def _warm_single_key(self, key: str, loader: Callable[[str], Any]) -> None:
        """Warm single cache key."""
        try:
            # Check if already cached
            existing = await self.get(key)
            if existing is not None:
                return
            
            # Load and cache value
            if asyncio.iscoroutinefunction(loader):
                value = await loader(key)
            else:
                value = loader(key)
            
            await self.set(key, value)
            
        except Exception as e:
            logger.error(f"Cache key warming error for {sanitize_log_input(key)}: {sanitize_log_input(str(e))}")
    
    def get_statistics(self) -> Dict[str, CacheStatistics]:
        """Get combined cache statistics."""
        return {
            'memory': self.memory_cache.stats,
            'disk': self.disk_cache.stats,
            'combined': CacheStatistics(
                hits=self.memory_cache.stats.hits + self.disk_cache.stats.hits,
                misses=self.memory_cache.stats.misses + self.disk_cache.stats.misses,
                evictions=self.memory_cache.stats.evictions + self.disk_cache.stats.evictions,
                total_size=self.memory_cache.stats.total_size + self.disk_cache.stats.total_size,
                item_count=self.memory_cache.stats.item_count
            )
        }
    
    async def clear_all(self) -> None:
        """Clear all caches."""
        await self.memory_cache.clear()
        
        try:
            for cache_file in self.disk_cache.cache_dir.glob("*.cache"):
                cache_file.unlink(missing_ok=True)
            self.disk_cache.stats = CacheStatistics()
        except Exception as e:
            logger.error(f"Cache clear error: {sanitize_log_input(str(e))}")


# Global cache manager instance
cache_manager = CacheManager()