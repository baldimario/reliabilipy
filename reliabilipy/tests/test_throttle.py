import time
import threading
import pytest

from reliabilipy import throttle, Throttled


def test_throttle_sleep_mode_rate_limiting():
    calls = []

    @throttle(calls=2, period=0.5, burst=2, mode="sleep")
    def f(i):
        calls.append((i, time.monotonic()))

    t0 = time.monotonic()
    for i in range(4):
        f(i)
    elapsed = time.monotonic() - t0
    # With 2 calls per 0.5s: first 2 immediate, next 2 should take ~0.5s extra
    assert elapsed >= 0.45


def test_throttle_raise_mode_exceeds_limit():
    @throttle(calls=1, period=0.5, mode="raise")
    def g():
        return True

    assert g() is True
    with pytest.raises(Throttled):
        g()
    # After sleeping for period, it should succeed again
    time.sleep(0.55)
    assert g() is True


def test_throttle_burst_capacity():
    results = []

    @throttle(calls=2, period=1.0, burst=4, mode="raise")
    def h(i):
        results.append(i)

    # First 4 should pass due to burst capacity
    for i in range(4):
        h(i)

    # 5th should be throttled immediately
    with pytest.raises(Throttled):
        h(4)
