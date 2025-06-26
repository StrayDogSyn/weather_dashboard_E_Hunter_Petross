"""Cache service implementation."""

import time
import logging
from typing import Any, Optional, Dict
from threading import Lock

from ..interfaces.weather_interfaces import ICacheService


class MemoryCacheService(ICacheService):
    """In-memory cache service implementation."""
    
    def __init__(self):
        """Initialize the memory cache."""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        
        logging.info("Memory cache service initialized")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            cache_entry = self._cache[key]
            current_time = time.time()
            
            # Check if expired
            if current_time > cache_entry['expires_at']:
                del self._cache[key]
                logging.debug(f"Cache entry expired and removed: {key}")
                return None
            
            logging.debug(f"Cache hit: {key}")
            return cache_entry['value']
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set cached value with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        try:
            with self._lock:
                expires_at = time.time() + ttl
                self._cache[key] = {
                    'value': value,
                    'expires_at': expires_at,
                    'created_at': time.time()
                }
            
            logging.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logging.error(f"Error setting cache entry {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete cached value.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful
        """
        try:
            with self._lock:
                if key in self._cache:
                    del self._cache[key]
                    logging.debug(f"Cache entry deleted: {key}")
                    return True
                else:
                    logging.debug(f"Cache entry not found for deletion: {key}")
                    return False
                    
        except Exception as e:
            logging.error(f"Error deleting cache entry {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all cached values.
        
        Returns:
            True if successful
        """
        try:
            with self._lock:
                cache_size = len(self._cache)
                self._cache.clear()
            
            logging.info(f"Cache cleared: {cache_size} entries removed")
            return True
            
        except Exception as e:
            logging.error(f"Error clearing cache: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = []
        
        with self._lock:
            for key, cache_entry in self._cache.items():
                if current_time > cache_entry['expires_at']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
        
        if expired_keys:
            logging.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        with self._lock:
            current_time = time.time()
            total_entries = len(self._cache)
            expired_entries = sum(
                1 for entry in self._cache.values() 
                if current_time > entry['expires_at']
            )
            
            return {
                'total_entries': total_entries,
                'active_entries': total_entries - expired_entries,
                'expired_entries': expired_entries,
                'cache_keys': list(self._cache.keys())
            }
    
    def get_cache_key(self, prefix: str, *args) -> str:
        """
        Generate a cache key from prefix and arguments.
        
        Args:
            prefix: Key prefix
            *args: Arguments to include in key
            
        Returns:
            Generated cache key
        """
        key_parts = [str(prefix)]
        key_parts.extend(str(arg) for arg in args)
        return ":".join(key_parts)
