"""Tests for the metrics module."""
import pytest
from prometheus_client import REGISTRY
from reliabilipy import observe, MetricsCollector, ReliabilityMetricsMiddleware

@pytest.fixture
def metrics():
    # Store original collectors
    original_collectors = set(REGISTRY._collector_to_names.keys())
    
    collector = MetricsCollector(namespace="test")
    yield collector
    
    # Clear test metrics after each test
    current_collectors = set(REGISTRY._collector_to_names.keys())
    new_collectors = current_collectors - original_collectors
    
    for metric in new_collectors:
        try:
            REGISTRY.unregister(metric)
        except KeyError:
            pass  # Ignore if metric is already unregistered

def test_function_duration_tracking(metrics):
    @observe(name="test_func", metrics=metrics)
    def test_function():
        return "done"
    
    test_function()
    
    # Check that metrics were recorded
    duration = REGISTRY.get_sample_value(
        "test_function_duration_seconds_count",
        {"function": "test_func"}
    )
    assert duration == 1

def test_retry_metrics(metrics):
    metrics.retry_attempts.labels(
        function="test_retry",
        exception="ValueError"
    ).inc()
    
    value = REGISTRY.get_sample_value(
        "test_retry_attempts_total",
        {"function": "test_retry", "exception": "ValueError"}
    )
    assert value == 1

def test_circuit_breaker_metrics(metrics):
    metrics.circuit_state.labels(
        function="test_circuit"
    ).set(2)  # Set to CLOSED state
    
    value = REGISTRY.get_sample_value(
        "test_circuit_state",
        {"function": "test_circuit"}
    )
    assert value == 2

def test_state_operation_metrics(metrics):
    metrics.state_operations.labels(
        operation="set",
        backend="redis"
    ).inc()
    
    value = REGISTRY.get_sample_value(
        "test_state_operations_total",
        {"operation": "set", "backend": "redis"}
    )
    assert value == 1

async def test_web_middleware_metrics():
    async def mock_app(scope, receive, send):
        return None

    middleware = ReliabilityMetricsMiddleware(
        app=mock_app
    )
    
    # Mock web request
    scope = {"type": "http", "method": "GET"}
    
    await middleware(scope, None, None)
    
    # Verify request duration was recorded
    duration = REGISTRY.get_sample_value(
        "reliabilipy_function_duration_seconds_count",
        {"function": "http_GET"}
    )
    assert duration == 1
