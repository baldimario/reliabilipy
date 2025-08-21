# Retry

The `retry` decorator retries a function call on specified exceptions using configurable backoff strategies.

## API

`retry(exceptions=(Exception,), backoff='exponential', max_retries=3, jitter=False, base_delay=1.0, max_delay=60.0)`

- `exceptions`: Exception type or tuple to retry on. Use the most specific types possible.
- `backoff`: `'exponential'` or `'linear'`.
  - Exponential: delay = `min(base_delay * 2^(attempt-1), max_delay)`
  - Linear: delay = `min(base_delay * attempt, max_delay)`
- `max_retries`: Maximum retry attempts after the initial call.
- `jitter`: When `True`, multiplies the delay by a factor in `[0.5, 1.5)`. Defaults to `False` for deterministic tests.
- `base_delay`: Base delay in seconds.
- `max_delay`: Maximum allowed delay in seconds.

## Usage

```python
from reliabilipy import retry

@retry(exceptions=(ConnectionError,), backoff='exponential', max_retries=5, base_delay=0.2)
def fetch():
    ...
```

## Best Practices

- Choose exception types carefully to avoid masking programming errors.
- Use exponential backoff for network operations; linear for predictable pacing.
- Add `jitter=True` in distributed systems to reduce thundering herd.
- Set reasonable `max_retries` and `max_delay` to avoid long stalls.
