#!/usr/bin/env python3
"""
Module for caching data with Redis and tracking method calls
"""

import redis
import uuid
from typing import Union, Optional, Callable
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count how many times a method is called.

    Stores the count in Redis using the method's qualified name.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Increments the call count and calls the method"""
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a method.

    Inputs and outputs are stored as Redis lists with keys:
    "<method_qualname>:inputs" and "<method_qualname>:outputs"
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Store stringified input arguments (ignore kwargs)
        self._redis.rpush(input_key, str(args))

        # Call the original method
        output = method(self, *args, **kwargs)

        # Store output
        self._redis.rpush(output_key, output)

        return output

    return wrapper


def replay(method: Callable):
    """
    Display the history of calls of a particular method.

    Args:
        method: The decorated method to replay history for.
    """
    # Redis client is accessible through the method's __self__ (the instance)
    redis_client = method.__self__._redis
    method_name = method.__qualname__

    # Keys for inputs and outputs lists
    inputs_key = f"{method_name}:inputs"
    outputs_key = f"{method_name}:outputs"

    # Get the call count
    call_count = redis_client.get(method_name)
    call_count = int(call_count) if call_count else 0
    print(f"{method_name} was called {call_count} times:")

    # Retrieve inputs and outputs lists
    inputs = redis_client.lrange(inputs_key, 0, -1)
    outputs = redis_client.lrange(outputs_key, 0, -1)

    # Iterate over inputs and outputs and display each call
    for inp, out in zip(inputs, outputs):
        # Decode bytes to strings
        inp_str = inp.decode("utf-8")
        out_str = out.decode("utf-8") if isinstance(out, bytes) else str(out)
        print(f"{method_name}(*{inp_str}) -> {out_str}")


class Cache:
    """Cache class for storing data in Redis"""

    def __init__(self):
        """Initialize the Redis client and flush the DB"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the given data in Redis using a random key.

        Args:
            data: The data to store (str, bytes, int, or float)

        Returns:
            The generated key (str)
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
        self, key: str, fn: Optional[Callable] = None
    ) -> Union[bytes, str, int, None]:
        """
        Retrieve value from Redis and optionally apply conversion function

        Args:
            key: Redis key to retrieve
            fn: Optional function to convert the result

        Returns:
            The value (raw or converted), or None if key is not found
        """
        value = self._redis.get(key)
        if value is None:
            return None
        return fn(value) if fn else value

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a string value from Redis by decoding bytes

        Args:
            key: Redis key

        Returns:
            The string value or None
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer value from Redis

        Args:
            key: Redis key

        Returns:
            The integer value or None
        """
        return self.get(key, fn=int)
    