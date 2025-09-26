import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.services.performance_monitoring import get_performance_monitor

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track request performance metrics."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.monitor = None
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Record metric
        try:
            if self.monitor is None:
                # We need to get the monitor instance, but we don't have access to the database session here
                # This is a limitation of the current design
                pass
            else:
                # Determine if request was successful
                success = 200 <= response.status_code < 400
                self.monitor.record_request(duration, success)
        except Exception as e:
            logger.error(f"Error recording request metric: {e}")
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.2f}ms"
        response.headers["X-Request-ID"] = str(int(start_time * 1000000))
        
        return response

class DatabasePerformanceMiddleware:
    """Middleware to track database query performance."""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.monitor = None
    
    def record_query(self, duration: float):
        """Record a database query metric."""
        try:
            if self.monitor is None:
                self.monitor = get_performance_monitor(self.db_session)
            self.monitor.record_database_query(duration)
        except Exception as e:
            logger.error(f"Error recording database query metric: {e}")

class WebSocketPerformanceMiddleware:
    """Middleware to track WebSocket performance."""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.monitor = None
    
    def record_connection(self, connected: bool = True):
        """Record a WebSocket connection metric."""
        try:
            if self.monitor is None:
                self.monitor = get_performance_monitor(self.db_session)
            self.monitor.record_websocket_connection(connected)
        except Exception as e:
            logger.error(f"Error recording WebSocket connection metric: {e}")
    
    def record_message(self, sent: bool = True):
        """Record a WebSocket message metric."""
        try:
            if self.monitor is None:
                self.monitor = get_performance_monitor(self.db_session)
            self.monitor.record_websocket_message(sent)
        except Exception as e:
            logger.error(f"Error recording WebSocket message metric: {e}")

class CachePerformanceMiddleware:
    """Middleware to track cache performance."""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.monitor = None
    
    def record_hit(self, hit: bool = True):
        """Record a cache hit/miss metric."""
        try:
            if self.monitor is None:
                self.monitor = get_performance_monitor(self.db_session)
            self.monitor.record_cache_hit(hit)
        except Exception as e:
            logger.error(f"Error recording cache metric: {e}")

# Performance decorators
def track_performance(func):
    """Decorator to track function performance."""
    import functools
    import time
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.info(f"Function {func.__name__} completed in {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Function {func.__name__} failed after {duration:.2f}ms: {e}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.info(f"Function {func.__name__} completed in {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Function {func.__name__} failed after {duration:.2f}ms: {e}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def track_database_performance(func):
    """Decorator to track database query performance."""
    import functools
    import time
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.info(f"Database query {func.__name__} completed in {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Database query {func.__name__} failed after {duration:.2f}ms: {e}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.info(f"Database query {func.__name__} completed in {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Database query {func.__name__} failed after {duration:.2f}ms: {e}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def track_cache_performance(func):
    """Decorator to track cache performance."""
    import functools
    import time
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.info(f"Cache operation {func.__name__} completed in {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Cache operation {func.__name__} failed after {duration:.2f}ms: {e}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.info(f"Cache operation {func.__name__} completed in {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Cache operation {func.__name__} failed after {duration:.2f}ms: {e}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
