"""
Circuit breaker pattern implementation to prevent repeated calls to failing services.
"""
from functools import wraps
import time
from typing import Callable, Optional, Type, Union, Tuple
from enum import Enum
from .metrics import default_metrics

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Service calls blocked
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = (Exception,),
        metrics=None
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.exceptions = exceptions
        self.metrics = metrics or default_metrics
        self.function_name = None
        
        self.failures = 0
        self.last_failure_time = 0
        self.state = CircuitState.CLOSED  # Initialize state directly first
    
    def can_execute(self) -> bool:
        """Check if the circuit breaker allows execution."""
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self._set_state(CircuitState.HALF_OPEN)
                return True
            return False
            
        return True  # HALF_OPEN state allows one test request
    
    def _set_state(self, new_state: CircuitState) -> None:
        """Update circuit breaker state and record metric."""
        self.state = new_state
        if self.function_name:
            # Update gauge with numeric state value
            state_value = {
                CircuitState.OPEN: 0,
                CircuitState.HALF_OPEN: 1,
                CircuitState.CLOSED: 2
            }[new_state]
            self.metrics.circuit_state.labels(function=self.function_name).set(state_value)
    
    def record_success(self) -> None:
        """Record a successful execution."""
        self.failures = 0
        if self.state == CircuitState.HALF_OPEN:
            self._set_state(CircuitState.CLOSED)
    
    def record_failure(self) -> None:
        """Record a failed execution."""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.function_name:
            self.metrics.circuit_failures.labels(function=self.function_name).inc()
        
        if self.failures >= self.failure_threshold:
            self._set_state(CircuitState.OPEN)

def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = (Exception,),
    metrics=None
) -> Callable:
    """
    Decorator that implements the circuit breaker pattern.
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery
        exceptions: Exception types to catch and count as failures
    
    Returns:
        Decorated function with circuit breaker protection
    """
    breaker = CircuitBreaker(failure_threshold, recovery_timeout, exceptions, metrics=metrics)
    
    def decorator(func: Callable) -> Callable:
        # Set function name and initialize metrics
        breaker.function_name = func.__name__
        # Initialize circuit state metric with function name
        breaker.metrics.circuit_state.labels(function=func.__name__).set(2)  # 2 = CLOSED
        breaker.metrics.circuit_failures.labels(function=func.__name__).inc(0)  # Initialize counter
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not breaker.can_execute():
                raise RuntimeError("Circuit breaker is open")
            
            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except breaker.exceptions as e:
                breaker.record_failure()
                raise
                
        return wrapper
    return decorator
