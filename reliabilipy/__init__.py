"""
reliabilipy - A comprehensive Python library for building reliable software
"""

from .retry import retry
from .state import StateManager
from .circuit_breaker import circuit_breaker
from .timeout import with_timeout, TimeoutError
from .safeguards import assert_invariant, require, ensure, InvariantViolation
from .failure_injection import inject_failure, inject_latency
from .metrics import observe, MetricsCollector, ReliabilityMetricsMiddleware
from .throttle import throttle, Throttled

__version__ = "0.1.0"

__all__ = [
    # Retry functionality
    "retry",
    
    # State management
    "StateManager",
    
    # Circuit breaker
    "circuit_breaker",
    
    # Timeout handling
    "with_timeout",
    "TimeoutError",
    
    # Assertions and safeguards
    "assert_invariant",
    "require",
    "ensure",
    "InvariantViolation",
    
    # Failure injection for testing
    "inject_failure",
    "inject_latency",
    
    # Metrics and observability
    "observe",
    "MetricsCollector",
    "ReliabilityMetricsMiddleware"
    ,
    # Throttling
    "throttle",
    "Throttled",
]
