"""Tests for the safeguards module."""
import pytest
from reliabilipy import assert_invariant, require, ensure, InvariantViolation

def test_assert_invariant():
    state = {'users': 500}
    
    # Should pass
    assert_invariant(
        lambda: state['users'] < 1000,
        "Too many users"
    )
    
    # Should fail
    state['users'] = 1500
    with pytest.raises(InvariantViolation, match="Too many users"):
        assert_invariant(
            lambda: state['users'] < 1000,
            "Too many users"
        )

def test_assert_invariant_with_fallback():
    state = {'users': 1500}
    fallback_called = False
    
    def fallback():
        nonlocal fallback_called
        fallback_called = True
        state['users'] = 900
    
    with pytest.raises(InvariantViolation):
        assert_invariant(
            lambda: state['users'] < 1000,
            "Too many users",
            fallback=fallback
        )
    
    assert fallback_called
    assert state['users'] == 900

def test_require_decorator():
    state = {'authenticated': False}
    
    @require(lambda: state['authenticated'], "Must be authenticated")
    def protected_function():
        return "secret data"
    
    with pytest.raises(InvariantViolation, match="Must be authenticated"):
        protected_function()
    
    state['authenticated'] = True
    assert protected_function() == "secret data"

def test_ensure_decorator():
    @ensure(lambda result: result > 0, "Result must be positive")
    def positive_number(n):
        return n
    
    assert positive_number(5) == 5
    
    with pytest.raises(InvariantViolation, match="Result must be positive"):
        positive_number(-1)

def test_combined_decorators():
    state = {'authenticated': True}
    
    @require(lambda: state['authenticated'], "Must be authenticated")
    @ensure(lambda result: len(result) > 0, "Result cannot be empty")
    def get_user_data():
        return ["data"]
    
    assert get_user_data() == ["data"]
    
    # Test precondition failure
    state['authenticated'] = False
    with pytest.raises(InvariantViolation, match="Must be authenticated"):
        get_user_data()
