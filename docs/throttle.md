# Throttle (Rate Limiting)

Limit call rates using a thread-safe token-bucket algorithm.

## API

`throttle(calls, period=1.0, *, burst=None, mode='sleep', exception=Throttled)`

- `calls`: Allowed calls per `period`.
- `period`: Window length in seconds.
- `burst`: Optional bucket capacity; defaults to `calls`.
- `mode`: `'sleep'` to block until a token is available, `'raise'` to raise `Throttled`.
- `exception`: Exception class to raise in `raise` mode.

## Usage

```python
from reliabilipy import throttle, Throttled

@throttle(calls=10, period=1.0, burst=10, mode='sleep')
def handle():
    ...

@throttle(calls=2, period=1.0, mode='raise')
def call_api():
    ...
```

## Notes

- Thread-safe; a single bucket shared across decorator instances for that function.
- For distributed rate limiting, use an external service like Redis-based limiters.
