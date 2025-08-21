# Metrics and Observability

Prometheus-based metrics for reliability features and function timings.

## Components

- `MetricsCollector(namespace='reliabilipy')` with counters, gauges, and histograms.
- `observe(name=None, metrics=None)` decorator to time functions and log exceptions.
- `ReliabilityMetricsMiddleware(app, metrics=None)` for simple ASGI integration.

## Usage

```python
from reliabilipy import observe, MetricsCollector
from prometheus_client import start_http_server

start_http_server(8000)
metrics = MetricsCollector(namespace='myapp')

@observe(name='process', metrics=metrics)
def process():
    ...
```

## Exported Metrics

- `*_function_duration_seconds` (Histogram)
- `*_retry_attempts_total` (Counter)
- `*_retry_success_total` (Counter)
- `*_circuit_state` (Gauge)
- `*_circuit_failures_total` (Counter)
- `*_state_operations_total` (Counter)
- `*_state_errors_total` (Counter)
