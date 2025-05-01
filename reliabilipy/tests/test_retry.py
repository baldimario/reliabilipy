"""Tests for the retry module."""
import pytest
from reliabilipy import retry
import time

def test_retry_with_exponential_backoff():
    attempts = []
    
    @retry(exceptions=(ValueError,), backoff='exponential', max_retries=3)
    def failing_function():
        attempts.append(time.time())
        raise ValueError("Intentional failure")
    
    with pytest.raises(ValueError):
        failing_function()
    
    assert len(attempts) == 4  # Initial try + 3 retries
    
    # Check exponential backoff timing
    intervals = [attempts[i+1] - attempts[i] for i in range(len(attempts)-1)]
    assert all(intervals[i] > intervals[i-1] for i in range(1, len(intervals)))

def test_retry_success_after_failure():
    attempts = 0
    
    @retry(exceptions=(ValueError,), max_retries=3)
    def eventually_succeeds():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Not yet")
        return "success"
    
    result = eventually_succeeds()
    assert result == "success"
    assert attempts == 3

def test_retry_with_specific_exceptions():
    @retry(exceptions=(ValueError,), max_retries=2)
    def raise_type_error():
        raise TypeError("Wrong type")
    
    with pytest.raises(TypeError):  # Should not retry on TypeError
        raise_type_error()

def test_retry_with_jitter():
    delays = []
    
    @retry(exceptions=(ValueError,), backoff='exponential', max_retries=3, jitter=True)
    def failing_with_jitter():
        delays.append(time.time())
        raise ValueError("Fail with jitter")
    
    with pytest.raises(ValueError):
        failing_with_jitter()
    
    # With jitter, delays should not be exactly exponential
    intervals = [delays[i+1] - delays[i] for i in range(len(delays)-1)]
    base_intervals = [1, 2, 4]  # Expected base intervals without jitter
    
    # Check that intervals are not exactly matching base exponential pattern
    assert not any(abs(i1 - i2) < 0.01 for i1, i2 in zip(intervals, base_intervals))

def test_retry_max_retries():
    attempts = 0
    
    @retry(max_retries=2)
    def always_fails():
        nonlocal attempts
        attempts += 1
        raise ValueError("Always fails")
    
    with pytest.raises(ValueError):
        always_fails()
    
    assert attempts == 3  # Initial attempt + 2 retries
