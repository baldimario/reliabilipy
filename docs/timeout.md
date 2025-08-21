# Timeout

Apply a timeout to a function call with an optional fallback.

Note: Uses POSIX timers (`signal.setitimer`); only works in the main thread on Unix-like OS.

## API

`with_timeout(timeout, fallback=None)`

- `timeout`: Seconds before raising `TimeoutError`.
- `fallback`: Value or callable to return when timed out.

## Usage

```python
from reliabilipy import with_timeout, TimeoutError

@with_timeout(timeout=2.0, fallback=lambda: "default")
def slow():
    ...
```

## Tips

- For multi-threaded or Windows environments, consider cooperative cancellation rather than signals.
