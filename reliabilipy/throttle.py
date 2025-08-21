"""
Throttle decorator to rate-limit function calls.

Implements a lightweight token-bucket rate limiter that can either sleep
until a token is available or raise an exception when the limit is exceeded.
"""
import time
import threading
from functools import wraps
from typing import Callable, Optional, Type


class Throttled(Exception):
    """Raised when a throttled function exceeds the allowed rate in raise mode."""


class _TokenBucket:
    def __init__(self, rate_per_sec: float, capacity: int, clock: Callable[[], float] = time.monotonic):
        # rate: tokens added per second
        self.rate = float(rate_per_sec)
        self.capacity = int(max(1, capacity))
        self._tokens = float(self.capacity)
        self._timestamp = clock()
        self._clock = clock
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = self._clock()
        elapsed = max(0.0, now - self._timestamp)
        if elapsed > 0:
            self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
            self._timestamp = now

    def consume_or_wait(self) -> None:
        with self._lock:
            self._refill()
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return
            # Need to wait for the deficit to be refilled
            deficit = 1.0 - self._tokens
            wait_time = deficit / self.rate if self.rate > 0 else float("inf")
        if wait_time > 0:
            time.sleep(wait_time)
        # After sleeping, attempt to consume again recursively (tail path is short)
        with self._lock:
            self._refill()
            if self._tokens < 1.0:
                # Should be extremely rare due to race, but guard anyway
                deficit = 1.0 - self._tokens
                extra_wait = deficit / self.rate if self.rate > 0 else float("inf")
                if extra_wait > 0:
                    time.sleep(extra_wait)
                    self._refill()
            self._tokens = max(0.0, self._tokens - 1.0)

    def try_consume(self) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return True
            return False


def throttle(
    calls: int,
    period: float = 1.0,
    *,
    burst: Optional[int] = None,
    mode: str = "sleep",
    exception: Type[Exception] = Throttled,
) -> Callable:
    """
    Decorator to throttle function calls using a token-bucket algorithm.

    Args:
        calls: Allowed number of calls per given period.
        period: Time window length in seconds.
        burst: Maximum burst size (bucket capacity). Defaults to `calls`.
        mode: 'sleep' to block until allowed, or 'raise' to raise immediately.
        exception: Exception type to raise when in 'raise' mode and throttled.

    Returns:
        A decorated function that is rate-limited.
    """
    if calls <= 0:
        raise ValueError("calls must be > 0")
    if period <= 0:
        raise ValueError("period must be > 0")
    if mode not in ("sleep", "raise"):
        raise ValueError("mode must be 'sleep' or 'raise'")

    capacity = burst if burst is not None else calls
    rate_per_sec = float(calls) / float(period)

    bucket = _TokenBucket(rate_per_sec=rate_per_sec, capacity=capacity)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if mode == "sleep":
                bucket.consume_or_wait()
            else:  # raise mode
                if not bucket.try_consume():
                    raise exception("Rate limit exceeded")
            return func(*args, **kwargs)

        return wrapper

    return decorator
