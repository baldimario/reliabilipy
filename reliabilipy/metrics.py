"""
Metrics and observability system for monitoring reliability features.
"""
from typing import Optional, Dict, Any
from prometheus_client import Counter, Histogram, Gauge
import time
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and exports metrics for reliability features."""
    
    def __init__(self, namespace: str = "reliabilipy"):
        """Initialize metrics collector with Prometheus metrics."""
        self.namespace = namespace
        
        # Retry metrics
        self.retry_attempts = Counter(
            f"{namespace}_retry_attempts_total",
            "Total number of retry attempts",
            ["function", "exception"]
        )
        self.retry_success = Counter(
            f"{namespace}_retry_success_total",
            "Total number of successful retries",
            ["function"]
        )
        
        # Circuit breaker metrics
        self.circuit_state = Gauge(
            f"{namespace}_circuit_state",
            "Circuit breaker state (0=open, 1=half-open, 2=closed)",
            ["function"]
        )
        self.circuit_failures = Counter(
            f"{namespace}_circuit_failures_total",
            "Total number of circuit breaker failures",
            ["function"]
        )
        
        # State management metrics
        self.state_operations = Counter(
            f"{namespace}_state_operations_total",
            "Total number of state operations",
            ["operation", "backend"]
        )
        self.state_errors = Counter(
            f"{namespace}_state_errors_total",
            "Total number of state operation errors",
            ["operation", "backend"]
        )
        
        # Function execution timing
        self.function_duration = Histogram(
            f"{namespace}_function_duration_seconds",
            "Function execution duration in seconds",
            ["function"]
        )

class ObservabilityDecorator:
    """Decorator for adding observability to functions."""
    
    def __init__(
        self,
        metrics: MetricsCollector,
        function_name: Optional[str] = None
    ):
        self.metrics = metrics
        self.function_name = function_name
    
    def __call__(self, func):
        fname = self.function_name or func.__name__
        
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                with self.metrics.function_duration.labels(fname).time():
                    result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.exception(f"Function {fname} failed with error: {str(e)}")
                raise
            finally:
                duration = time.time() - start_time
                logger.info(f"Function {fname} took {duration:.2f} seconds")
        
        return wrapper

# Global metrics collector instance
default_metrics = MetricsCollector()

def observe(
    name: Optional[str] = None,
    metrics: Optional[MetricsCollector] = None
):
    """
    Decorator for adding observability to functions.
    
    Args:
        name: Optional custom name for the function in metrics
        metrics: Optional custom metrics collector instance
    """
    return ObservabilityDecorator(
        metrics or default_metrics,
        name
    )

class ReliabilityMetricsMiddleware:
    """Middleware for collecting reliability metrics in web applications."""
    
    def __init__(
        self,
        app,
        metrics: Optional[MetricsCollector] = None
    ):
        self.app = app
        self.metrics = metrics or default_metrics
    
    async def __call__(self, scope, receive, send):
        start_time = time.time()
        
        try:
            if self.app is None:
                return None
            if callable(self.app):
                response = await self.app(scope, receive, send)
                return response
            return None
        finally:
            duration = time.time() - start_time
            if scope.get("type") == "http" and scope.get("method"):
                # Record request metrics
                self.metrics.function_duration.labels(
                    f"http_{scope['method']}"
                ).observe(duration)
