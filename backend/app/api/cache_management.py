from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.services.cache_service import get_cache_service, CacheManager
from app.api.auth import get_current_user

router = APIRouter()

class CacheSetRequest(BaseModel):
    key: str
    value: Any
    ttl: Optional[int] = None

class CacheSetMultipleRequest(BaseModel):
    mapping: Dict[str, Any]
    ttl: Optional[int] = None

@router.get("/stats")
async def get_cache_stats(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cache statistics."""
    try:
        cache_service = get_cache_service()
        stats = cache_service.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/keys/{key}")
async def get_cache_value(
    key: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a cache value by key."""
    try:
        cache_service = get_cache_service()
        value = cache_service.get(key)
        
        if value is None:
            raise HTTPException(status_code=404, detail="Key not found")
        
        return {
            "success": True,
            "key": key,
            "value": value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/keys")
async def set_cache_value(
    request: CacheSetRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set a cache value."""
    try:
        cache_service = get_cache_service()
        success = cache_service.set(request.key, request.value, request.ttl)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to set cache value")
        
        return {
            "success": True,
            "key": request.key,
            "message": "Cache value set successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/keys/{key}")
async def delete_cache_value(
    key: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a cache value."""
    try:
        cache_service = get_cache_service()
        success = cache_service.delete(key)
        
        if not success:
            raise HTTPException(status_code=404, detail="Key not found")
        
        return {
            "success": True,
            "key": key,
            "message": "Cache value deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/keys/{key}/exists")
async def check_cache_key_exists(
    key: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if a cache key exists."""
    try:
        cache_service = get_cache_service()
        exists = cache_service.exists(key)
        
        return {
            "success": True,
            "key": key,
            "exists": exists
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/keys/{key}/ttl")
async def get_cache_ttl(
    key: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get TTL for a cache key."""
    try:
        cache_service = get_cache_service()
        ttl = cache_service.get_ttl(key)
        
        return {
            "success": True,
            "key": key,
            "ttl": ttl
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/keys/{key}/expire")
async def set_cache_ttl(
    key: str,
    ttl: int = Query(..., description="TTL in seconds"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set TTL for a cache key."""
    try:
        cache_service = get_cache_service()
        success = cache_service.expire(key, ttl)
        
        if not success:
            raise HTTPException(status_code=404, detail="Key not found")
        
        return {
            "success": True,
            "key": key,
            "ttl": ttl,
            "message": "TTL set successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/keys/multiple")
async def set_multiple_cache_values(
    request: CacheSetMultipleRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set multiple cache values."""
    try:
        cache_service = get_cache_service()
        success = cache_service.set_multiple(request.mapping, request.ttl)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to set cache values")
        
        return {
            "success": True,
            "keys": list(request.mapping.keys()),
            "message": "Cache values set successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/keys/multiple")
async def get_multiple_cache_values(
    keys: str = Query(..., description="Comma-separated list of keys"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get multiple cache values."""
    try:
        key_list = [key.strip() for key in keys.split(",")]
        cache_service = get_cache_service()
        values = cache_service.get_multiple(key_list)
        
        return {
            "success": True,
            "values": values
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/keys/multiple")
async def delete_multiple_cache_values(
    keys: str = Query(..., description="Comma-separated list of keys"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete multiple cache values."""
    try:
        key_list = [key.strip() for key in keys.split(",")]
        cache_service = get_cache_service()
        deleted_count = cache_service.delete_multiple(key_list)
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Deleted {deleted_count} cache values"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/pattern/{pattern}")
async def clear_cache_pattern(
    pattern: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all cache keys matching a pattern."""
    try:
        cache_service = get_cache_service()
        deleted_count = cache_service.clear_pattern(pattern)
        
        return {
            "success": True,
            "pattern": pattern,
            "deleted_count": deleted_count,
            "message": f"Deleted {deleted_count} cache keys matching pattern"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invalidate/user/{user_id}")
async def invalidate_user_cache(
    user_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invalidate all cache entries for a user."""
    try:
        cache_manager = CacheManager(get_cache_service())
        deleted_count = cache_manager.invalidate_user_cache(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "deleted_count": deleted_count,
            "message": f"Invalidated {deleted_count} cache entries for user"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invalidate/symbol/{symbol}")
async def invalidate_symbol_cache(
    symbol: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invalidate all cache entries for a symbol."""
    try:
        cache_manager = CacheManager(get_cache_service())
        deleted_count = cache_manager.invalidate_symbol_cache(symbol)
        
        return {
            "success": True,
            "symbol": symbol,
            "deleted_count": deleted_count,
            "message": f"Invalidated {deleted_count} cache entries for symbol"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/warm")
async def warm_cache(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Warm cache with data for multiple symbols."""
    try:
        symbol_list = [symbol.strip() for symbol in symbols.split(",")]
        cache_manager = CacheManager(get_cache_service())
        results = cache_manager.warm_cache(symbol_list)
        
        return {
            "success": True,
            "symbols": symbol_list,
            "results": results,
            "message": "Cache warming completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def cache_health_check(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check cache service health."""
    try:
        cache_service = get_cache_service()
        stats = cache_service.get_stats()
        
        is_healthy = stats.get("connected", False)
        
        return {
            "success": True,
            "healthy": is_healthy,
            "stats": stats
        }
        
    except Exception as e:
        return {
            "success": False,
            "healthy": False,
            "error": str(e)
        }

@router.post("/flush")
async def flush_all_cache(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Flush all cache (admin only)."""
    try:
        # In a real implementation, you would check if the user is an admin
        # For now, we'll allow any authenticated user to flush cache
        
        cache_service = get_cache_service()
        if cache_service.connected:
            cache_service.redis_client.flushdb()
        
        return {
            "success": True,
            "message": "All cache flushed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
