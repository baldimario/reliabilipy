"""
Failure injection tools for chaos engineering and reliability testing.
"""
import random
from functools import wraps
from typing import Callable, Optional, Type, Union, List

class FailureInjector:
    """Manages failure injection for chaos engineering tests."""
    
    def __init__(
        self,
        rate: float = 0.1,
        exception: Type[Exception] = RuntimeError,
        message: str = "Injected failure"
    ):
        """
        Initialize failure injector.
        
        Args:
            rate: Probability of failure (0.0 to 1.0)
            exception: Exception type to raise
            message: Custom error message for injected failures
        """
        if not 0 <= rate <= 1:
            raise ValueError("Failure rate must be between 0 and 1")
        self.rate = rate
        self.exception = exception
        self.message = message
        self.enabled = True
    
    def should_fail(self) -> bool:
        """Determine if this call should fail."""
        return random.random() < self.rate
    
    def __call__(self, func: Callable) -> Callable:
        """Make the injector usable as a decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if failure injection is disabled
            if hasattr(func, 'enabled') and not func.enabled:
                return func(*args, **kwargs)
            if self.should_fail():
                raise self.exception(self.message)
            return func(*args, **kwargs)
        # Initialize enabled flag on the original function
        func.enabled = True
        return wrapper

def inject_failure(
    rate: float = 0.1,
    exception: Type[Exception] = RuntimeError,
    message: str = "Injected failure"
) -> Callable:
    """
    Decorator that randomly injects failures into function calls.
    
    Args:
        rate: Probability of failure (0.0 to 1.0)
        exception: Exception type to raise
        message: Custom error message for injected failures
    """
    injector = FailureInjector(rate, exception, message)
    return injector

class LatencyInjector:
    """Injects random latency into function calls."""
    
    def __init__(
        self,
        min_delay: float = 0.1,
        max_delay: float = 1.0,
        rate: float = 1.0
    ):
        """
        Initialize latency injector.
        
        Args:
            min_delay: Minimum delay in seconds
            max_delay: Maximum delay in seconds
            rate: Probability of adding latency (0.0 to 1.0)
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.rate = rate
        self.enabled = True
    
    def get_delay(self) -> float:
        """Calculate the delay to inject."""
        if not self.enabled or random.random() >= self.rate:
            return 0
        return random.uniform(self.min_delay, self.max_delay)
    
    def __call__(self, func: Callable) -> Callable:
        """Make the injector usable as a decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = self.get_delay()
            if delay > 0:
                import time
                time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper

def inject_latency(
    min_delay: float = 0.1,
    max_delay: float = 1.0,
    rate: float = 1.0
) -> Callable:
    """
    Decorator that adds random latency to function calls.
    
    Args:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds
        rate: Probability of adding latency (0.0 to 1.0)
    """
    injector = LatencyInjector(min_delay, max_delay, rate)
    return injector
