"""Tests for the failure injection module."""
import pytest
import time
from reliabilipy import inject_failure, inject_latency

def test_failure_injection_rate():
    successes = 0
    failures = 0
    
    @inject_failure(rate=0.5, exception=ValueError, message="Injected failure")
    def flaky_function():
        return "success"
    
    # Run multiple times to test probability
    for _ in range(100):
        try:
            result = flaky_function()
            assert result == "success"
            successes += 1
        except ValueError as e:
            assert str(e) == "Injected failure"
            failures += 1
    
    # With rate=0.5, expect roughly equal successes and failures
    # Allow for some statistical variation
    assert 30 <= failures <= 70
    assert successes + failures == 100

def test_failure_injection_disabled():
    @inject_failure(rate=1.0, exception=ValueError)
    def always_fails():
        return "success"
    
    # Should always fail when enabled
    with pytest.raises(ValueError):
        always_fails()
    
    # Disable failure injection
    always_fails.__wrapped__.enabled = False
    assert always_fails() == "success"

def test_latency_injection():
    @inject_latency(min_delay=0.1, max_delay=0.2)
    def slow_function():
        return "done"
    
    start_time = time.time()
    result = slow_function()
    duration = time.time() - start_time
    
    assert result == "done"
    assert 0.1 <= duration <= 0.2

def test_latency_injection_rate():
    times = []
    
    @inject_latency(min_delay=0.1, max_delay=0.1, rate=0.5)
    def sometimes_slow():
        return "done"
    
    for _ in range(20):
        start = time.time()
        sometimes_slow()
        duration = time.time() - start
        times.append(duration)
    
    # Some calls should be fast (near zero latency)
    # Some calls should be slow (around 0.1s)
    fast_calls = len([t for t in times if t < 0.05])
    slow_calls = len([t for t in times if t >= 0.05])
    
    assert 5 <= fast_calls <= 15
    assert 5 <= slow_calls <= 15
    assert fast_calls + slow_calls == 20
