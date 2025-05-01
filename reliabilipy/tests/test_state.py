"""Tests for the state management module."""
import pytest
import os
import json
import fakeredis
from reliabilipy import StateManager

@pytest.fixture
def temp_file_path(tmp_path):
    return str(tmp_path / "test_state.json")

@pytest.fixture
def redis_client():
    return fakeredis.FakeStrictRedis()

def test_file_state_manager(temp_file_path):
    state = StateManager(backend='file', namespace='test', file_path=temp_file_path)
    
    # Test setting and getting values
    state.set("key1", "value1")
    state.set("key2", {"nested": "value"})
    
    assert state.get("key1") == "value1"
    assert state.get("key2") == {"nested": "value"}
    
    # Test persistence
    state2 = StateManager(backend='file', namespace='test', file_path=temp_file_path)
    assert state2.get("key1") == "value1"
    
    # Test delete
    state.delete("key1")
    assert state.get("key1") is None

def test_redis_state_manager(monkeypatch, redis_client):
    def mock_from_url(*args, **kwargs):
        return redis_client
    
    # Mock redis.from_url to use our fake redis
    monkeypatch.setattr("redis.from_url", mock_from_url)
    
    state = StateManager(backend='redis', namespace='test')
    
    # Test setting and getting values
    state.set("key1", "value1")
    state.set("key2", {"nested": "value"})
    
    assert state.get("key1") == "value1"
    assert state.get("key2") == {"nested": "value"}
    
    # Test namespacing
    raw_key = "test:key1"
    assert redis_client.exists(raw_key)
    
    # Test delete
    state.delete("key1")
    assert state.get("key1") is None
    assert not redis_client.exists(raw_key)

def test_state_manager_clear(temp_file_path):
    state = StateManager(backend='file', namespace='test', file_path=temp_file_path)
    
    # Set multiple values
    state.set("key1", "value1")
    state.set("key2", "value2")
    
    # Clear all values
    state.clear()
    
    assert state.get("key1") is None
    assert state.get("key2") is None

def test_state_manager_serialization(temp_file_path):
    state = StateManager(backend='file', namespace='test', file_path=temp_file_path)
    
    complex_data = {
        "string": "value",
        "number": 42,
        "list": [1, 2, 3],
        "nested": {"key": "value"}
    }
    
    state.set("complex", complex_data)
    retrieved = state.get("complex")
    
    assert retrieved == complex_data
    
    # Verify raw file content is valid JSON
    with open(temp_file_path, 'r') as f:
        raw_data = json.load(f)
        assert isinstance(raw_data, dict)
