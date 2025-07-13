#!/usr/bin/env python3
"""
Module: exercise.py
Defines a Cache class to interact with Redis.
"""
import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
    def __init__(self):
        """Initialize Redis client and flush the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis with a randomly generated key.

        Args:
            data: The data to be stored (str, bytes, int, float).

        Returns:
            str: The key under which the data is stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """Retrieve data from Redis and optionally apply a conversion function.

        Args:
            key: The Redis key to look up.
            fn: Optional callable to convert the data back to its original format.

        Returns:
            The original data if found, optionally converted, otherwise None.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data
    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, None]:
        """Retrieve a value from Redis and optionally apply a conversion function."""
        value = self._redis.get(key)
        if value is None:
            return None
        if fn:
            return fn(value)
        return value

    def get_str(self, key: str) -> str:
        """Retrieve a string value from Redis."""
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Retrieve an int value from Redis."""
        return self.get(key, fn=int)

    def get_str(self, key: str) -> Optional[str]:
        """Retrieve a string from Redis.

        Args:
            key: The Redis key.

        Returns:
            The data decoded to string or None.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """Retrieve an integer from Redis.

        Args:
            key: The Redis key.

        Returns:
            The data converted to integer or None.
        """
        return self.get(key, fn=int)
