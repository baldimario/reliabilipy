# Failure Injection

Inject random failures and latency to test system resilience.

## API

`inject_failure(rate=0.1, exception=RuntimeError, message='Injected failure')`

- `rate`: Probability of raising `exception` per call (0..1).
- `exception`: Exception class to raise.
- `message`: Error message.

`inject_latency(min_delay=0.1, max_delay=1.0, rate=1.0)`

- `min_delay`: Minimum seconds to sleep when latency is injected.
- `max_delay`: Maximum seconds to sleep; internally capped slightly to avoid overshoot.
- `rate`: Probability of adding latency per call.

## Usage

```python
from reliabilipy import inject_failure, inject_latency

@inject_failure(rate=0.2, exception=TimeoutError)
def sometimes_fails():
    ...

@inject_latency(min_delay=0.05, max_delay=0.2, rate=0.5)
def sometimes_slow():
    ...
```

## Notes

- Use in non-production or controlled environments.
- Seed randomness for reproducible tests where appropriate.
