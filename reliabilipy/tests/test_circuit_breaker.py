"""Tests for the circuit breaker module."""
import pytest
import time
from reliabilipy import circuit_breaker
from reliabilipy.circuit_breaker import CircuitState

def test_circuit_breaker_basic_functionality():
    called_times = 0
    
    @circuit_breaker(failure_threshold=2, recovery_timeout=0.1)
    def failing_service():
        nonlocal called_times
        called_times += 1
        raise ConnectionError("Service unavailable")
    
    # First two calls should attempt and fail
    for _ in range(2):
        with pytest.raises(ConnectionError):
            failing_service()
    
    # Third call should raise circuit open
    with pytest.raises(RuntimeError) as exc_info:
        failing_service()
    assert "Circuit breaker is open" in str(exc_info.value)
    assert called_times == 2  # Should not have attempted third call

def test_circuit_breaker_recovery():
    successes = 0
    failures = 0
    
    @circuit_breaker(failure_threshold=2, recovery_timeout=0.1)
    def unstable_service():
        nonlocal successes, failures
        if failures < 2:
            failures += 1
            raise ConnectionError("Service down")
        successes += 1
        return "success"
    
    # Fail twice
    for _ in range(2):
        with pytest.raises(ConnectionError):
            unstable_service()
    
    # Wait for recovery timeout
    time.sleep(0.2)
    
    # Should work now
    result = unstable_service()
    assert result == "success"
    assert successes == 1
    assert failures == 2

def test_circuit_breaker_half_open_state():
    failures = 0
    
    @circuit_breaker(failure_threshold=2, recovery_timeout=0.1)
    def service():
        nonlocal failures
        failures += 1
        raise ConnectionError("Still failing")
    
    # Break the circuit
    for _ in range(2):
        with pytest.raises(ConnectionError):
            service()
    
    # Wait for recovery timeout
    time.sleep(0.2)
    
    # Circuit should be half-open, allowing one test request
    with pytest.raises(ConnectionError):
        service()
    
    # Should immediately open again
    with pytest.raises(RuntimeError) as exc_info:
        service()
    assert "Circuit breaker is open" in str(exc_info.value)
    assert failures == 3  # Initial 2 + 1 test request

def test_circuit_breaker_specific_exceptions():
    @circuit_breaker(failure_threshold=2, exceptions=(ValueError,))
    def service():
        raise ConnectionError("Different error")
    
    # Should not count towards circuit breaker
    for _ in range(3):
        with pytest.raises(ConnectionError):
            service()
        
    # Circuit should still be closed
    with pytest.raises(ConnectionError):
        service()
