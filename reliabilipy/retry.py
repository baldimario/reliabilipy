"""
Retry decorators with various backoff strategies and configurable options.
"""
from functools import wraps
import random
import time
from typing import Optional, Type, Union, Tuple, Callable
from .metrics import default_metrics

class RetryConfig:
    def __init__(
        self,
        exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = (Exception,),
        backoff: str = 'exponential',
        max_retries: int = 3,
        jitter: bool = False,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ):
        self.exceptions = exceptions
        self.backoff = backoff
        self.max_retries = max_retries
        self.jitter = jitter
        self.base_delay = base_delay
        self.max_delay = max_delay

def retry(
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = (Exception,),
    backoff: str = 'exponential',
    max_retries: int = 3,
    jitter: bool = False,
    base_delay: float = 1.0,
    max_delay: float = 60.0
) -> Callable:
    """
    A decorator that retries the function on failure with configurable backoff.
    
    Args:
        exceptions: Exception or tuple of exceptions to catch and retry on
        backoff: Type of backoff ('exponential' or 'linear')
        max_retries: Maximum number of retry attempts
        jitter: Whether to add randomness to delay
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
    
    Returns:
        Decorated function that will retry on specified exceptions
    """
    config = RetryConfig(exceptions, backoff, max_retries, jitter, base_delay, max_delay)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            function_name = func.__name__
            
            while True:
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:  # If we had retries but finally succeeded
                        default_metrics.retry_success.labels(function=function_name).inc()
                    return result
                except config.exceptions as e:
                    attempt += 1
                    if attempt > config.max_retries:
                        raise
                    
                    # Record retry attempt with exception type
                    default_metrics.retry_attempts.labels(
                        function=function_name,
                        exception=e.__class__.__name__
                    ).inc()
                    
                    if config.backoff == 'exponential':
                        delay = min(config.base_delay * (2 ** (attempt - 1)), config.max_delay)
                    else:  # linear
                        delay = min(config.base_delay * attempt, config.max_delay)
                    
                    if config.jitter:
                        delay *= (0.5 + random.random())
                    
                    time.sleep(delay)
                    
        return wrapper
    return decorator
