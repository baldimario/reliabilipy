# State Management

Persist and recover application state with file or Redis backends.

## API

`StateManager(backend='file', namespace='default', redis_url='redis://localhost:6379', file_path=None, serializer='json')`

- `backend`: `'file'` or `'redis'`.
- `namespace`: Prefix for keys.
- `redis_url`: Connection URL when using Redis.
- `file_path`: File path for file backend.
- `serializer`: `'json'` or `'pickle'`.

### Methods

- `set(key, value)`
- `get(key, default=None)`
- `delete(key)`
- `clear()`

## Usage

```python
from reliabilipy import StateManager

state = StateManager(backend='file', namespace='pipeline')
state.set('offset', 100)
offset = state.get('offset', 0)
```

## Tips

- Use Redis for concurrent or distributed workers.
- Prefer JSON for portability; use pickle for complex Python objects.
