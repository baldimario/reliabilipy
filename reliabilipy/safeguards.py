"""
Runtime assertions and safeguards for maintaining system invariants.
"""
from typing import Any, Callable, Optional
from functools import wraps

class InvariantViolation(Exception):
    """Raised when a system invariant is violated."""
    pass

def assert_invariant(
    condition: Callable[[], bool],
    message: Optional[str] = None,
    fallback: Optional[Callable[[], Any]] = None
) -> None:
    """
    Assert that a system invariant holds true.
    
    Args:
        condition: Function that returns True if invariant holds
        message: Custom error message if invariant fails
        fallback: Optional recovery function to call if invariant fails
    
    Raises:
        InvariantViolation: If the invariant check fails
    """
    if not condition():
        if fallback:
            fallback()
        raise InvariantViolation(message or "System invariant violated")

def require(
    precondition: Callable[[], bool],
    message: Optional[str] = None
) -> Callable:
    """
    Decorator to enforce preconditions on function calls.
    
    Args:
        precondition: Function that returns True if precondition holds
        message: Custom error message if precondition fails
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not precondition():
                raise InvariantViolation(message or "Precondition failed")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def ensure(
    postcondition: Callable[[Any], bool],
    message: Optional[str] = None
) -> Callable:
    """
    Decorator to enforce postconditions on function results.
    
    Args:
        postcondition: Function that takes the result and returns True if valid
        message: Custom error message if postcondition fails
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if not postcondition(result):
                raise InvariantViolation(message or "Postcondition failed")
            return result
        return wrapper
    return decorator
