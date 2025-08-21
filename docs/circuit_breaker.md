# Circuit Breaker

Prevents repeated calls to failing services by opening a circuit after consecutive failures.

## API

`circuit_breaker(failure_threshold=5, recovery_timeout=60.0, exceptions=(Exception,), metrics=None)`

- `failure_threshold`: Number of consecutive failures to open the circuit.
- `recovery_timeout`: Seconds to wait before trying a half-open test call.
- `exceptions`: Exception types counted as failures.
- `metrics`: Optional custom `MetricsCollector`.

States:
- Closed (normal)
- Open (reject calls)
- Half-open (allow one test call, then close on success or open on failure)

## Usage

```python
from reliabilipy import circuit_breaker

@circuit_breaker(failure_threshold=3, recovery_timeout=10.0, exceptions=(ConnectionError,))
def call_service():
    ...
```

## When to Use

- Protect dependencies that can fail or degrade.
- Prevent cascading failures.
- Combine with retry and timeout for robust remote calls.
