"""Tests for the timeout module."""
import pytest
import time
from reliabilipy import with_timeout, TimeoutError

def test_timeout_basic():
    @with_timeout(timeout=0.1)
    def slow_function():
        time.sleep(0.2)
        return "completed"
    
    with pytest.raises(TimeoutError):
        slow_function()

def test_timeout_with_fallback():
    @with_timeout(timeout=0.1, fallback="fallback_value")
    def slow_function():
        time.sleep(0.2)
        return "completed"
    
    result = slow_function()
    assert result == "fallback_value"

def test_timeout_with_fallback_function():
    @with_timeout(timeout=0.1, fallback=lambda: "computed_fallback")
    def slow_function():
        time.sleep(0.2)
        return "completed"
    
    result = slow_function()
    assert result == "computed_fallback"

def test_timeout_quick_execution():
    @with_timeout(timeout=1)
    def quick_function():
        return "completed"
    
    result = quick_function()
    assert result == "completed"

def test_timeout_nested():
    @with_timeout(timeout=0.2)
    def outer_function():
        @with_timeout(timeout=0.1)
        def inner_function():
            time.sleep(0.15)
            return "inner"
        return inner_function()
    
    with pytest.raises(TimeoutError):
        outer_function()
