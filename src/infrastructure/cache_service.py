"""Cache Service Implementation for Weather Dashboard.

This module provides caching functionality with TTL support,
persistence, and automatic cleanup for improved performance.
"""

import time
import json
import logging
import threading
from typing import Any, Optional, Dict, Set
from pathlib import Path
import pickle
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..business.interfaces import ICacheService
from ..shared.exceptions import CacheError
from ..shared.constants import DEFAULT_CACHE_TTL, CACHE_FILE_PATH


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    created_at: float
    ttl: int
    access_count: int = 0
    last_accessed: float = 0.0
    
    def __post_init__(self):
        if self.last_accessed == 0.0:
            self.last_accessed = self.created_at
    
    @property
    def is_expired(self) -> bool:
        """Check if the cache entry is expired."""
        return time.time() > (self.created_at + self.ttl)
    
    @property
    def age(self) -> float:
        """Get the age of the cache entry in seconds."""
        return time.time() - self.created_at
    
    def touch(self) -> None:
        """Update access metadata."""
        self.access_count += 1
        self.last_accessed = time.time()


class CacheService(ICacheService):
    """In-memory cache service with persistence and TTL support.
    
    Provides caching functionality with automatic expiration,
    LRU eviction, and optional persistence to disk.
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = DEFAULT_CACHE_TTL,
        cleanup_interval: int = 300,
        persistence_enabled: bool = True,
        persistence_file: Optional[str] = None
    ):
        """Initialize the cache service.
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
            cleanup_interval: Cleanup interval in seconds
            persistence_enabled: Whether to persist cache to disk
            persistence_file: Path to persistence file
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        
        # Configuration
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._cleanup_interval = cleanup_interval
        self._persistence_enabled = persistence_enabled
        self._persistence_file = persistence_file or CACHE_FILE_PATH
        
        # Cache storage
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        
        # Cleanup timer
        self._cleanup_timer: Optional[threading.Timer] = None
        self._running = False
        
        # Initialize
        self._start_cleanup_timer()
        if self._persistence_enabled:
            self._load_from_disk()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._misses += 1
                self._logger.debug(f"Cache miss for key: {key}")
                return None
            
            if entry.is_expired:
                del self._cache[key]
                self._misses += 1
                self._logger.debug(f"Cache expired for key: {key}")
                return None
            
            # Update access metadata
            entry.touch()
            self._hits += 1
            self._logger.debug(f"Cache hit for key: {key}")
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        effective_ttl = ttl if ttl is not None else self._default_ttl
        
        with self._lock:
            # Check if we need to evict entries
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_lru()
            
            # Create cache entry
            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                ttl=effective_ttl
            )
            
            self._cache[key] = entry
            self._logger.debug(f"Cached value for key: {key} (TTL: {effective_ttl}s)")
    
    async def delete(self, key: str) -> bool:
        """Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._logger.debug(f"Deleted cache key: {key}")
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
            self._logger.info("Cache cleared")
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and is not expired
        """
        with self._lock:
            entry = self._cache.get(key)
            return entry is not None and not entry.is_expired
    
    async def get_keys(self, pattern: Optional[str] = None) -> Set[str]:
        """Get all cache keys, optionally filtered by pattern.
        
        Args:
            pattern: Optional pattern to filter keys
            
        Returns:
            Set of cache keys
        """
        with self._lock:
            keys = set(self._cache.keys())
            
            if pattern:
                import fnmatch
                keys = {key for key in keys if fnmatch.fnmatch(key, pattern)}
            
            return keys
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self._max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': round(hit_rate, 2),
                'evictions': self._evictions,
                'memory_usage': self._estimate_memory_usage()
            }
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )
        
        del self._cache[lru_key]
        self._evictions += 1
        self._logger.debug(f"Evicted LRU entry: {lru_key}")
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                self._logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
    
    def _start_cleanup_timer(self) -> None:
        """Start the cleanup timer."""
        if self._running:
            return
        
        self._running = True
        self._schedule_cleanup()
    
    def _schedule_cleanup(self) -> None:
        """Schedule the next cleanup."""
        if not self._running:
            return
        
        self._cleanup_timer = threading.Timer(
            self._cleanup_interval,
            self._run_cleanup
        )
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
    
    def _run_cleanup(self) -> None:
        """Run cleanup and schedule next one."""
        try:
            self._cleanup_expired()
            if self._persistence_enabled:
                self._save_to_disk()
        except Exception as e:
            self._logger.error(f"Cleanup failed: {e}")
        finally:
            self._schedule_cleanup()
    
    def _save_to_disk(self) -> None:
        """Save cache to disk."""
        try:
            # Create directory if it doesn't exist
            Path(self._persistence_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for serialization
            cache_data = {
                'entries': {},
                'stats': {
                    'hits': self._hits,
                    'misses': self._misses,
                    'evictions': self._evictions
                },
                'timestamp': time.time()
            }
            
            # Only save non-expired entries
            for key, entry in self._cache.items():
                if not entry.is_expired:
                    cache_data['entries'][key] = {
                        'value': entry.value,
                        'created_at': entry.created_at,
                        'ttl': entry.ttl,
                        'access_count': entry.access_count,
                        'last_accessed': entry.last_accessed
                    }
            
            # Save to file
            with open(self._persistence_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            self._logger.debug(f"Cache saved to disk: {self._persistence_file}")
            
        except Exception as e:
            self._logger.error(f"Failed to save cache to disk: {e}")
    
    def _load_from_disk(self) -> None:
        """Load cache from disk."""
        try:
            if not Path(self._persistence_file).exists():
                self._logger.debug("No cache file found, starting with empty cache")
                return
            
            with open(self._persistence_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Restore entries
            for key, entry_data in cache_data.get('entries', {}).items():
                entry = CacheEntry(
                    value=entry_data['value'],
                    created_at=entry_data['created_at'],
                    ttl=entry_data['ttl'],
                    access_count=entry_data['access_count'],
                    last_accessed=entry_data['last_accessed']
                )
                
                # Only restore non-expired entries
                if not entry.is_expired:
                    self._cache[key] = entry
            
            # Restore stats
            stats = cache_data.get('stats', {})
            self._hits = stats.get('hits', 0)
            self._misses = stats.get('misses', 0)
            self._evictions = stats.get('evictions', 0)
            
            self._logger.info(f"Cache loaded from disk: {len(self._cache)} entries")
            
        except Exception as e:
            self._logger.error(f"Failed to load cache from disk: {e}")
            # Start with empty cache on load failure
            self._cache.clear()
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage of cache in bytes.
        
        Returns:
            Estimated memory usage in bytes
        """
        try:
            import sys
            total_size = 0
            
            for key, entry in self._cache.items():
                total_size += sys.getsizeof(key)
                total_size += sys.getsizeof(entry.value)
                total_size += sys.getsizeof(entry)
            
            return total_size
            
        except Exception:
            return 0
    
    def shutdown(self) -> None:
        """Shutdown the cache service."""
        self._running = False
        
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
        
        if self._persistence_enabled:
            self._save_to_disk()
        
        self._logger.info("Cache service shutdown")
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.shutdown()
        except Exception:
            pass  # Ignore errors during cleanup