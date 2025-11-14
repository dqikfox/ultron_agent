"""
ULTRON Agent 3.0 - Intelligent Cache Manager
Provides multi-tier caching with Redis and SQLite fallback
"""

import json
import sqlite3
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Dict, Tuple
from dataclasses import dataclass, asdict
import threading
from utils.ultron_logger import get_logger

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = get_logger("cache_manager")


@dataclass
class CacheEntry:
    """Represents a cached item"""
    key: str
    value: str
    created_at: float
    expires_at: float
    hit_count: int = 0
    size_bytes: int = 0


class CacheManager:
    """
    Multi-tier caching system with Redis primary and SQLite fallback.
    Provides intelligent cache eviction, statistics tracking, and persistence.
    """

    def __init__(self, 
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 sqlite_path: str = "cache/ultron_cache.db",
                 default_ttl: int = 3600,
                 max_memory_mb: int = 100):
        """
        Initialize cache manager
        
        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            sqlite_path: Path to SQLite database
            default_ttl: Default time-to-live in seconds
            max_memory_mb: Maximum memory usage in MB
        """
        self.default_ttl = default_ttl
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.sqlite_path = Path(sqlite_path)
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0
        }
        self._lock = threading.Lock()
        
        # Initialize Redis connection
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                logger.info(f"Redis cache connected at {redis_host}:{redis_port}")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, using SQLite only")
                self.redis_client = None
        else:
            logger.info("Redis not available, using SQLite cache only")
        
        # Initialize SQLite cache
        self._init_sqlite()
        
        logger.info(f"Cache manager initialized (TTL: {default_ttl}s, Max: {max_memory_mb}MB)")

    def _init_sqlite(self) -> None:
        """Initialize SQLite database for persistent caching"""
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.sqlite_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at REAL NOT NULL,
                expires_at REAL NOT NULL,
                hit_count INTEGER DEFAULT 0,
                size_bytes INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"SQLite cache initialized at {self.sqlite_path}")

    def _hash_key(self, key: str) -> str:
        """Generate consistent hash for cache key"""
        return hashlib.sha256(key.encode()).hexdigest()[:32]

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            hashed_key = self._hash_key(key)
            
            # Try Redis first
            if self.redis_client:
                try:
                    value = self.redis_client.get(f"ultron:{hashed_key}")
                    if value:
                        self.stats['hits'] += 1
                        logger.debug(f"Cache hit (Redis): {key[:50]}")
                        return json.loads(value)
                except Exception as e:
                    logger.warning(f"Redis get error: {e}")
            
            # Fallback to SQLite
            try:
                conn = sqlite3.connect(str(self.sqlite_path))
                cursor = conn.cursor()
                
                cursor.execute(
                    'SELECT value, expires_at, hit_count FROM cache WHERE key = ?',
                    (hashed_key,)
                )
                result = cursor.fetchone()
                
                if result:
                    value_str, expires_at, hit_count = result
                    
                    # Check expiration
                    if time.time() < expires_at:
                        # Update hit count
                        cursor.execute(
                            'UPDATE cache SET hit_count = ? WHERE key = ?',
                            (hit_count + 1, hashed_key)
                        )
                        conn.commit()
                        conn.close()
                        
                        self.stats['hits'] += 1
                        logger.debug(f"Cache hit (SQLite): {key[:50]}")
                        return json.loads(value_str)
                    else:
                        # Expired, delete it
                        cursor.execute('DELETE FROM cache WHERE key = ?', (hashed_key,))
                        conn.commit()
                        conn.close()
                        logger.debug(f"Cache expired: {key[:50]}")
                else:
                    conn.close()
                
            except Exception as e:
                logger.error(f"SQLite get error: {e}")
            
            self.stats['misses'] += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store value in cache
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time-to-live in seconds (None uses default)
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            try:
                hashed_key = self._hash_key(key)
                value_str = json.dumps(value)
                size_bytes = len(value_str.encode())
                ttl = ttl or self.default_ttl
                
                created_at = time.time()
                expires_at = created_at + ttl
                
                # Store in Redis
                if self.redis_client:
                    try:
                        self.redis_client.setex(
                            f"ultron:{hashed_key}",
                            ttl,
                            value_str
                        )
                        logger.debug(f"Cached to Redis: {key[:50]} ({size_bytes} bytes)")
                    except Exception as e:
                        logger.warning(f"Redis set error: {e}")
                
                # Store in SQLite
                conn = sqlite3.connect(str(self.sqlite_path))
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO cache 
                    (key, value, created_at, expires_at, hit_count, size_bytes)
                    VALUES (?, ?, ?, ?, 0, ?)
                ''', (hashed_key, value_str, created_at, expires_at, size_bytes))
                
                conn.commit()
                conn.close()
                
                self.stats['sets'] += 1
                logger.debug(f"Cached to SQLite: {key[:50]} ({size_bytes} bytes)")
                
                # Check if we need to evict old entries
                self._evict_if_needed()
                
                return True
                
            except Exception as e:
                logger.error(f"Cache set error: {e}")
                return False

    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        with self._lock:
            hashed_key = self._hash_key(key)
            deleted = False
            
            # Delete from Redis
            if self.redis_client:
                try:
                    self.redis_client.delete(f"ultron:{hashed_key}")
                    deleted = True
                except Exception as e:
                    logger.warning(f"Redis delete error: {e}")
            
            # Delete from SQLite
            try:
                conn = sqlite3.connect(str(self.sqlite_path))
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cache WHERE key = ?', (hashed_key,))
                conn.commit()
                conn.close()
                deleted = True
            except Exception as e:
                logger.error(f"SQLite delete error: {e}")
            
            if deleted:
                self.stats['deletes'] += 1
            
            return deleted

    def clear(self) -> bool:
        """Clear all cached entries"""
        with self._lock:
            # Clear Redis
            if self.redis_client:
                try:
                    # Delete all keys matching ultron:*
                    for key in self.redis_client.scan_iter("ultron:*"):
                        self.redis_client.delete(key)
                    logger.info("Redis cache cleared")
                except Exception as e:
                    logger.warning(f"Redis clear error: {e}")
            
            # Clear SQLite
            try:
                conn = sqlite3.connect(str(self.sqlite_path))
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cache')
                conn.commit()
                conn.close()
                logger.info("SQLite cache cleared")
                return True
            except Exception as e:
                logger.error(f"SQLite clear error: {e}")
                return False

    def _evict_if_needed(self) -> None:
        """Evict old entries if cache is too large"""
        try:
            conn = sqlite3.connect(str(self.sqlite_path))
            cursor = conn.cursor()
            
            # Check current size
            cursor.execute('SELECT SUM(size_bytes) FROM cache')
            total_size = cursor.fetchone()[0] or 0
            
            if total_size > self.max_memory_bytes:
                # Evict least recently used entries
                cursor.execute('''
                    DELETE FROM cache WHERE key IN (
                        SELECT key FROM cache 
                        ORDER BY hit_count ASC, created_at ASC 
                        LIMIT 100
                    )
                ''')
                evicted = cursor.rowcount
                conn.commit()
                
                self.stats['evictions'] += evicted
                logger.info(f"Evicted {evicted} cache entries (size: {total_size/1024/1024:.2f}MB)")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Cache eviction error: {e}")

    def cleanup_expired(self) -> int:
        """Remove expired entries from cache"""
        with self._lock:
            try:
                conn = sqlite3.connect(str(self.sqlite_path))
                cursor = conn.cursor()
                
                current_time = time.time()
                cursor.execute('DELETE FROM cache WHERE expires_at < ?', (current_time,))
                deleted = cursor.rowcount
                
                conn.commit()
                conn.close()
                
                if deleted > 0:
                    logger.info(f"Cleaned up {deleted} expired cache entries")
                
                return deleted
                
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
                return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            # Calculate hit rate
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            # Get SQLite stats
            try:
                conn = sqlite3.connect(str(self.sqlite_path))
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*), SUM(size_bytes) FROM cache')
                count, total_size = cursor.fetchone()
                count = count or 0
                total_size = total_size or 0
                
                conn.close()
                
            except Exception:
                count = 0
                total_size = 0
            
            return {
                'hit_rate': f"{hit_rate:.2f}%",
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'sets': self.stats['sets'],
                'deletes': self.stats['deletes'],
                'evictions': self.stats['evictions'],
                'entries': count,
                'size_mb': f"{total_size / 1024 / 1024:.2f}",
                'redis_connected': self.redis_client is not None
            }


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


# Convenience functions
def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    return get_cache_manager().get(key)


def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set value in cache"""
    return get_cache_manager().set(key, value, ttl)


def cache_delete(key: str) -> bool:
    """Delete value from cache"""
    return get_cache_manager().delete(key)


def cache_clear() -> bool:
    """Clear all cache"""
    return get_cache_manager().clear()


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return get_cache_manager().get_stats()
