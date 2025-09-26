import logging
import json
import pickle
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import redis
from functools import wraps
import hashlib
import asyncio
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        """Initialize cache service with Redis backend."""
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=False,  # We'll handle encoding/decoding manually
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            self.connected = True
            logger.info("Cache service connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            self.connected = False
    
    def _serialize(self, data: Any) -> bytes:
        """Serialize data for storage."""
        try:
            if isinstance(data, (str, int, float, bool)):
                return json.dumps(data).encode('utf-8')
            else:
                return pickle.dumps(data)
        except Exception as e:
            logger.error(f"Error serializing data: {e}")
            return pickle.dumps(data)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize data from storage."""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                # Fall back to pickle
                return pickle.loads(data)
            except Exception as e:
                logger.error(f"Error deserializing data: {e}")
                return None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments."""
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
        
        # Add keyword arguments
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}:{v}")
            else:
                key_parts.append(f"{k}:{hashlib.md5(str(v).encode()).hexdigest()[:8]}")
        
        return ":".join(key_parts)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a cache value with optional TTL."""
        if not self.connected:
            return False
        
        try:
            serialized_value = self._serialize(value)
            if ttl:
                return self.redis_client.setex(key, ttl, serialized_value)
            else:
                return self.redis_client.set(key, serialized_value)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a cache value."""
        if not self.connected:
            return None
        
        try:
            data = self.redis_client.get(key)
            if data is None:
                return None
            return self._deserialize(data)
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a cache key."""
        if not self.connected:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a cache key exists."""
        if not self.connected:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for an existing key."""
        if not self.connected:
            return False
        
        try:
            return bool(self.redis_client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Error setting TTL for cache key {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """Get TTL for a key."""
        if not self.connected:
            return -1
        
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL for cache key {key}: {e}")
            return -1
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a numeric value."""
        if not self.connected:
            return None
        
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {e}")
            return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement a numeric value."""
        if not self.connected:
            return None
        
        try:
            return self.redis_client.decrby(key, amount)
        except Exception as e:
            logger.error(f"Error decrementing cache key {key}: {e}")
            return None
    
    def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple cache values."""
        if not self.connected:
            return {}
        
        try:
            values = self.redis_client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = self._deserialize(value)
            return result
        except Exception as e:
            logger.error(f"Error getting multiple cache keys: {e}")
            return {}
    
    def set_multiple(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple cache values."""
        if not self.connected:
            return False
        
        try:
            serialized_mapping = {k: self._serialize(v) for k, v in mapping.items()}
            if ttl:
                # Use pipeline for atomic operations
                pipe = self.redis_client.pipeline()
                for key, value in serialized_mapping.items():
                    pipe.setex(key, ttl, value)
                pipe.execute()
            else:
                self.redis_client.mset(serialized_mapping)
            return True
        except Exception as e:
            logger.error(f"Error setting multiple cache keys: {e}")
            return False
    
    def delete_multiple(self, keys: List[str]) -> int:
        """Delete multiple cache keys."""
        if not self.connected:
            return 0
        
        try:
            return self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Error deleting multiple cache keys: {e}")
            return 0
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern."""
        if not self.connected:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.connected:
            return {"connected": False}
        
        try:
            info = self.redis_client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"connected": False, "error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate."""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0

# Global cache service instance
cache_service: Optional[CacheService] = None

def get_cache_service() -> CacheService:
    """Get or create cache service instance."""
    global cache_service
    if cache_service is None:
        cache_service = CacheService()
    return cache_service

def cached(ttl: int = 300, key_prefix: str = "cache"):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_service()
            
            # Generate cache key
            cache_key = cache._generate_key(key_prefix, func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache = get_cache_service()
            
            # Generate cache key
            cache_key = cache._generate_key(key_prefix, func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    return decorator

class CacheManager:
    """High-level cache manager for specific use cases."""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
    
    def cache_market_data(self, symbol: str, data: Any, ttl: int = 60) -> bool:
        """Cache market data for a symbol."""
        key = f"market_data:{symbol}"
        return self.cache.set(key, data, ttl)
    
    def get_cached_market_data(self, symbol: str) -> Optional[Any]:
        """Get cached market data for a symbol."""
        key = f"market_data:{symbol}"
        return self.cache.get(key)
    
    def cache_portfolio_data(self, user_id: str, data: Any, ttl: int = 300) -> bool:
        """Cache portfolio data for a user."""
        key = f"portfolio:{user_id}"
        return self.cache.set(key, data, ttl)
    
    def get_cached_portfolio_data(self, user_id: str) -> Optional[Any]:
        """Get cached portfolio data for a user."""
        key = f"portfolio:{user_id}"
        return self.cache.get(key)
    
    def cache_technical_indicators(self, symbol: str, data: Any, ttl: int = 300) -> bool:
        """Cache technical indicators for a symbol."""
        key = f"technical:{symbol}"
        return self.cache.set(key, data, ttl)
    
    def get_cached_technical_indicators(self, symbol: str) -> Optional[Any]:
        """Get cached technical indicators for a symbol."""
        key = f"technical:{symbol}"
        return self.cache.get(key)
    
    def cache_news_data(self, symbol: str, data: Any, ttl: int = 600) -> bool:
        """Cache news data for a symbol."""
        key = f"news:{symbol}"
        return self.cache.set(key, data, ttl)
    
    def get_cached_news_data(self, symbol: str) -> Optional[Any]:
        """Get cached news data for a symbol."""
        key = f"news:{symbol}"
        return self.cache.get(key)
    
    def invalidate_user_cache(self, user_id: str) -> int:
        """Invalidate all cache entries for a user."""
        patterns = [
            f"portfolio:{user_id}",
            f"user:{user_id}:*",
            f"alerts:{user_id}",
            f"watchlist:{user_id}"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            total_deleted += self.cache.clear_pattern(pattern)
        
        return total_deleted
    
    def invalidate_symbol_cache(self, symbol: str) -> int:
        """Invalidate all cache entries for a symbol."""
        patterns = [
            f"market_data:{symbol}",
            f"technical:{symbol}",
            f"news:{symbol}",
            f"*:{symbol}:*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            total_deleted += self.cache.clear_pattern(pattern)
        
        return total_deleted
    
    def warm_cache(self, symbols: List[str]) -> Dict[str, bool]:
        """Warm cache with data for multiple symbols."""
        results = {}
        for symbol in symbols:
            # This would typically call the actual data services
            # For now, we'll just mark as successful
            results[symbol] = True
        return results
