"""
State management module for persisting and recovering application state.
"""
import json
import os
import pickle
from typing import Any, Optional, Union
import redis

class StateManager:
    """
    Manages application state with support for multiple storage backends.
    """
    def __init__(
        self,
        backend: str = 'file',
        namespace: str = 'default',
        redis_url: str = 'redis://localhost:6379',
        file_path: Optional[str] = None,
        serializer: str = 'json'
    ):
        """
        Initialize state manager with specified backend.
        
        Args:
            backend: Storage backend ('file', 'redis', or 'sqlite')
            namespace: Namespace for state isolation
            redis_url: Redis connection URL if using redis backend
            file_path: Path to state file if using file backend
            serializer: Data serialization format ('json' or 'pickle')
        """
        self.backend = backend
        self.namespace = namespace
        self.serializer = serializer
        
        if backend == 'redis':
            self._client = redis.from_url(redis_url)
        elif backend == 'file':
            self.file_path = file_path or f'.reliabilipy_state_{namespace}.json'
            self._ensure_file_exists()
        else:
            raise ValueError(f"Unsupported backend: {backend}")
    
    def _ensure_file_exists(self) -> None:
        """Ensure the state file exists and is initialized."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({}, f)
    
    def _serialize(self, value: Any) -> str:
        """Serialize value to string."""
        if self.serializer == 'json':
            return json.dumps(value)
        return pickle.dumps(value)
    
    def _deserialize(self, value: Union[str, bytes]) -> Any:
        """Deserialize value from string."""
        if self.serializer == 'json':
            return json.loads(value)
        return pickle.loads(value)
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in the state store."""
        full_key = f"{self.namespace}:{key}"
        serialized = self._serialize(value)
        
        if self.backend == 'redis':
            self._client.set(full_key, serialized)
        else:
            with open(self.file_path, 'r+') as f:
                data = json.load(f)
                data[full_key] = serialized
                f.seek(0)
                json.dump(data, f)
                f.truncate()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the state store."""
        full_key = f"{self.namespace}:{key}"
        
        try:
            if self.backend == 'redis':
                value = self._client.get(full_key)
                if value is None:
                    return default
                return self._deserialize(value)
            else:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    value = data.get(full_key)
                    if value is None:
                        return default
                    return self._deserialize(value)
        except (json.JSONDecodeError, pickle.PickleError):
            return default
    
    def delete(self, key: str) -> None:
        """Delete a value from the state store."""
        full_key = f"{self.namespace}:{key}"
        
        if self.backend == 'redis':
            self._client.delete(full_key)
        else:
            with open(self.file_path, 'r+') as f:
                data = json.load(f)
                data.pop(full_key, None)
                f.seek(0)
                json.dump(data, f)
                f.truncate()
    
    def clear(self) -> None:
        """Clear all values in the current namespace."""
        if self.backend == 'redis':
            keys = self._client.keys(f"{self.namespace}:*")
            if keys:
                self._client.delete(*keys)
        else:
            with open(self.file_path, 'r+') as f:
                data = json.load(f)
                # Remove all keys in the current namespace
                data = {k: v for k, v in data.items() if not k.startswith(f"{self.namespace}:")}
                f.seek(0)
                json.dump(data, f)
                f.truncate()
