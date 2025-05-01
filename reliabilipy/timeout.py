"""
Timeout and fallback functionality for function calls.
"""
import signal
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union

T = TypeVar('T')

class TimeoutError(Exception):
    """Raised when a function call times out."""
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Function call timed out")

def with_timeout(
    timeout: float,
    fallback: Optional[Union[Callable[[], T], T]] = None
) -> Callable:
    """
    Decorator that applies a timeout to a function call with optional fallback.
    
    Args:
        timeout: Maximum time in seconds to wait for function completion
        fallback: Value or function to call if timeout occurs
    
    Returns:
        Decorated function with timeout protection
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            def handler(signum, frame):
                raise TimeoutError("Function call timed out")

            # Set up the timeout using SIGALRM
            original_handler = signal.signal(signal.SIGALRM, handler)
            # Convert float seconds to int seconds and microseconds
            seconds = int(timeout)
            microseconds = int((timeout - seconds) * 1_000_000)
            signal.setitimer(signal.ITIMER_REAL, timeout)
            
            try:
                result = func(*args, **kwargs)
                signal.setitimer(signal.ITIMER_REAL, 0)  # Disable timer
                signal.signal(signal.SIGALRM, original_handler)  # Restore handler
                return result
            except TimeoutError:
                signal.setitimer(signal.ITIMER_REAL, 0)  # Disable timer
                signal.signal(signal.SIGALRM, original_handler)  # Restore handler
                if fallback is None:
                    raise
                if callable(fallback):
                    return fallback()
                return fallback
                
        return wrapper
    return decorator
