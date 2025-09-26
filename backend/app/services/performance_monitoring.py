import logging
import time
import psutil
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json
import threading
from sqlalchemy.orm import Session

from app.db import models

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    timestamp: datetime
    metric_type: str
    value: float
    unit: str
    tags: Dict[str, str] = None

@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_sent_mb: float
    network_recv_mb: float
    load_average: List[float]
    timestamp: datetime

@dataclass
class ApplicationMetrics:
    """Application performance metrics."""
    request_count: int
    request_duration_avg: float
    request_duration_p95: float
    request_duration_p99: float
    error_rate: float
    active_connections: int
    websocket_connections: int
    cache_hit_rate: float
    cache_memory_usage: float
    database_connections: int
    database_query_time_avg: float
    timestamp: datetime

@dataclass
class BusinessMetrics:
    """Business performance metrics."""
    total_users: int
    active_users: int
    total_portfolios: int
    total_transactions: int
    total_orders: int
    total_alerts: int
    total_models: int
    total_posts: int
    total_likes: int
    total_comments: int
    total_follows: int
    timestamp: datetime

class PerformanceMonitor:
    """Performance monitoring service."""
    
    def __init__(self, db: Session):
        self.db = db
        self.metrics_history: deque = deque(maxlen=10000)  # Keep last 10k metrics
        self.system_metrics_history: deque = deque(maxlen=1000)  # Keep last 1k system metrics
        self.application_metrics_history: deque = deque(maxlen=1000)  # Keep last 1k app metrics
        self.business_metrics_history: deque = deque(maxlen=100)  # Keep last 100 business metrics
        
        # Request tracking
        self.request_times: deque = deque(maxlen=10000)
        self.error_count = 0
        self.request_count = 0
        
        # WebSocket tracking
        self.websocket_connections = 0
        self.websocket_messages_sent = 0
        self.websocket_messages_received = 0
        
        # Cache tracking
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Database tracking
        self.db_query_times: deque = deque(maxlen=1000)
        self.db_connections = 0
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background performance monitoring."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop background performance monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self.system_metrics_history.append(system_metrics)
                
                # Collect application metrics
                app_metrics = self._collect_application_metrics()
                self.application_metrics_history.append(app_metrics)
                
                # Collect business metrics
                business_metrics = self._collect_business_metrics()
                self.business_metrics_history.append(business_metrics)
                
                # Wait before next collection
                time.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
                time.sleep(60)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_total_mb = memory.total / (1024 * 1024)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_total_gb = disk.total / (1024 * 1024 * 1024)
            
            # Network metrics
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / (1024 * 1024)
            network_recv_mb = network.bytes_recv / (1024 * 1024)
            
            # Load average
            load_average = list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_total_mb=memory_total_mb,
                disk_usage_percent=disk_usage_percent,
                disk_used_gb=disk_used_gb,
                disk_total_gb=disk_total_gb,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                load_average=load_average,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                cpu_percent=0, memory_percent=0, memory_used_mb=0, memory_total_mb=0,
                disk_usage_percent=0, disk_used_gb=0, disk_total_gb=0,
                network_sent_mb=0, network_recv_mb=0, load_average=[0, 0, 0],
                timestamp=datetime.now()
            )
    
    def _collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application performance metrics."""
        try:
            # Request metrics
            request_duration_avg = 0
            request_duration_p95 = 0
            request_duration_p99 = 0
            
            if self.request_times:
                sorted_times = sorted(self.request_times)
                request_duration_avg = sum(sorted_times) / len(sorted_times)
                request_duration_p95 = sorted_times[int(len(sorted_times) * 0.95)]
                request_duration_p99 = sorted_times[int(len(sorted_times) * 0.99)]
            
            # Error rate
            error_rate = (self.error_count / max(self.request_count, 1)) * 100
            
            # Cache hit rate
            cache_hit_rate = (self.cache_hits / max(self.cache_hits + self.cache_misses, 1)) * 100
            
            # Database metrics
            db_query_time_avg = 0
            if self.db_query_times:
                db_query_time_avg = sum(self.db_query_times) / len(self.db_query_times)
            
            return ApplicationMetrics(
                request_count=self.request_count,
                request_duration_avg=request_duration_avg,
                request_duration_p95=request_duration_p95,
                request_duration_p99=request_duration_p99,
                error_rate=error_rate,
                active_connections=self.websocket_connections,
                websocket_connections=self.websocket_connections,
                cache_hit_rate=cache_hit_rate,
                cache_memory_usage=0,  # Would need Redis info
                database_connections=self.db_connections,
                database_query_time_avg=db_query_time_avg,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return ApplicationMetrics(
                request_count=0, request_duration_avg=0, request_duration_p95=0, request_duration_p99=0,
                error_rate=0, active_connections=0, websocket_connections=0, cache_hit_rate=0,
                cache_memory_usage=0, database_connections=0, database_query_time_avg=0,
                timestamp=datetime.now()
            )
    
    def _collect_business_metrics(self) -> BusinessMetrics:
        """Collect business performance metrics."""
        try:
            # User metrics
            total_users = self.db.query(models.User).count()
            active_users = self.db.query(models.User).filter(
                models.User.last_login >= datetime.now() - timedelta(days=7)
            ).count()
            
            # Portfolio metrics
            total_portfolios = self.db.query(models.Portfolio).count()
            
            # Transaction metrics
            total_transactions = self.db.query(models.Transaction).count()
            
            # Order metrics
            total_orders = self.db.query(models.Transaction).filter(
                models.Transaction.status == 'filled'
            ).count()
            
            # Alert metrics
            total_alerts = self.db.query(models.PriceAlert).filter(
                models.PriceAlert.is_active == True
            ).count()
            
            # ML model metrics
            total_models = self.db.query(models.MLModel).filter(
                models.MLModel.is_active == True
            ).count()
            
            # Social metrics
            total_posts = self.db.query(models.SocialPost).count()
            total_likes = self.db.query(models.SocialLike).count()
            total_comments = self.db.query(models.SocialComment).count()
            total_follows = self.db.query(models.SocialFollow).count()
            
            return BusinessMetrics(
                total_users=total_users,
                active_users=active_users,
                total_portfolios=total_portfolios,
                total_transactions=total_transactions,
                total_orders=total_orders,
                total_alerts=total_alerts,
                total_models=total_models,
                total_posts=total_posts,
                total_likes=total_likes,
                total_comments=total_comments,
                total_follows=total_follows,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error collecting business metrics: {e}")
            return BusinessMetrics(
                total_users=0, active_users=0, total_portfolios=0, total_transactions=0,
                total_orders=0, total_alerts=0, total_models=0, total_posts=0,
                total_likes=0, total_comments=0, total_follows=0,
                timestamp=datetime.now()
            )
    
    def record_request(self, duration: float, success: bool = True):
        """Record a request metric."""
        self.request_times.append(duration)
        self.request_count += 1
        if not success:
            self.error_count += 1
    
    def record_websocket_connection(self, connected: bool = True):
        """Record WebSocket connection metric."""
        if connected:
            self.websocket_connections += 1
        else:
            self.websocket_connections = max(0, self.websocket_connections - 1)
    
    def record_websocket_message(self, sent: bool = True):
        """Record WebSocket message metric."""
        if sent:
            self.websocket_messages_sent += 1
        else:
            self.websocket_messages_received += 1
    
    def record_cache_hit(self, hit: bool = True):
        """Record cache hit/miss metric."""
        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
    
    def record_database_query(self, duration: float):
        """Record database query metric."""
        self.db_query_times.append(duration)
    
    def record_database_connection(self, connected: bool = True):
        """Record database connection metric."""
        if connected:
            self.db_connections += 1
        else:
            self.db_connections = max(0, self.db_connections - 1)
    
    def get_system_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent system metrics."""
        return [asdict(metric) for metric in list(self.system_metrics_history)[-limit:]]
    
    def get_application_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent application metrics."""
        return [asdict(metric) for metric in list(self.application_metrics_history)[-limit:]]
    
    def get_business_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent business metrics."""
        return [asdict(metric) for metric in list(self.business_metrics_history)[-limit:]]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        latest_system = self.system_metrics_history[-1] if self.system_metrics_history else None
        latest_app = self.application_metrics_history[-1] if self.application_metrics_history else None
        latest_business = self.business_metrics_history[-1] if self.business_metrics_history else None
        
        return {
            "system": asdict(latest_system) if latest_system else None,
            "application": asdict(latest_app) if latest_app else None,
            "business": asdict(latest_business) if latest_business else None,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status."""
        latest_system = self.system_metrics_history[-1] if self.system_metrics_history else None
        latest_app = self.application_metrics_history[-1] if self.application_metrics_history else None
        
        health_status = {
            "overall": "healthy",
            "checks": {
                "cpu": "healthy",
                "memory": "healthy",
                "disk": "healthy",
                "requests": "healthy",
                "errors": "healthy",
                "cache": "healthy"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        if latest_system:
            # CPU health
            if latest_system.cpu_percent > 80:
                health_status["checks"]["cpu"] = "warning"
            elif latest_system.cpu_percent > 95:
                health_status["checks"]["cpu"] = "critical"
                health_status["overall"] = "degraded"
            
            # Memory health
            if latest_system.memory_percent > 80:
                health_status["checks"]["memory"] = "warning"
            elif latest_system.memory_percent > 95:
                health_status["checks"]["memory"] = "critical"
                health_status["overall"] = "degraded"
            
            # Disk health
            if latest_system.disk_usage_percent > 80:
                health_status["checks"]["disk"] = "warning"
            elif latest_system.disk_usage_percent > 95:
                health_status["checks"]["disk"] = "critical"
                health_status["overall"] = "degraded"
        
        if latest_app:
            # Request health
            if latest_app.request_duration_avg > 1000:  # 1 second
                health_status["checks"]["requests"] = "warning"
            elif latest_app.request_duration_avg > 5000:  # 5 seconds
                health_status["checks"]["requests"] = "critical"
                health_status["overall"] = "degraded"
            
            # Error health
            if latest_app.error_rate > 5:  # 5%
                health_status["checks"]["errors"] = "warning"
            elif latest_app.error_rate > 10:  # 10%
                health_status["checks"]["errors"] = "critical"
                health_status["overall"] = "degraded"
            
            # Cache health
            if latest_app.cache_hit_rate < 80:  # 80%
                health_status["checks"]["cache"] = "warning"
            elif latest_app.cache_hit_rate < 60:  # 60%
                health_status["checks"]["cache"] = "critical"
                health_status["overall"] = "degraded"
        
        return health_status
    
    def get_metrics_for_timeframe(self, start_time: datetime, end_time: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """Get metrics for a specific timeframe."""
        system_metrics = [
            asdict(metric) for metric in self.system_metrics_history
            if start_time <= metric.timestamp <= end_time
        ]
        
        app_metrics = [
            asdict(metric) for metric in self.application_metrics_history
            if start_time <= metric.timestamp <= end_time
        ]
        
        business_metrics = [
            asdict(metric) for metric in self.business_metrics_history
            if start_time <= metric.timestamp <= end_time
        ]
        
        return {
            "system": system_metrics,
            "application": app_metrics,
            "business": business_metrics
        }
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        if format == "json":
            return json.dumps({
                "system_metrics": self.get_system_metrics(),
                "application_metrics": self.get_application_metrics(),
                "business_metrics": self.get_business_metrics(),
                "exported_at": datetime.now().isoformat()
            }, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Global performance monitor instance
performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor(db: Session) -> PerformanceMonitor:
    """Get or create performance monitor instance."""
    global performance_monitor
    if performance_monitor is None:
        performance_monitor = PerformanceMonitor(db)
    return performance_monitor
