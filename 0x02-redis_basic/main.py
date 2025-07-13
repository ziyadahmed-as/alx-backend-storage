#!/usr/bin/env python3
"""
Main file to test Cache class
"""

import redis
Cache = __import__('exercise').Cache

cache = Cache()

# Test basic storing and raw retrieval
data = b"hello"
key = cache.store(data)
print(f"Stored key: {key}")

local_redis = redis.Redis()
print(f"Raw Redis value: {local_redis.get(key)}")

# Test get() with type recovery
TEST_CASES = {
    b"foo": None,
    123: int,
    "bar": lambda d: d.decode("utf-8")
}

for value, fn in TEST_CASES.items():
    key = cache.store(value)
    assert cache.get(key, fn=fn) == value, f"Failed for value: {value}"

print("All test cases passed!")

cache.store(b"first")
print(cache.get(cache.store.__qualname__))  # Expect b'1'

cache.store(b"second")
cache.store(b"third")
print(cache.get(cache.store.__qualname__))  # Expect b'3'

s1 = cache.store("first")
print(s1)
s2 = cache.store("secont")
print(s2)
s3 = cache.store("third")
print(s3)

inputs = cache._redis.lrange(f"{cache.store.__qualname__}:inputs", 0, -1)
outputs = cache._redis.lrange(f"{cache.store.__qualname__}:outputs", 0, -1)

print("inputs:", inputs)
print("outputs:", outputs)

cache.store("foo")
cache.store("bar")
cache.store(42)

replay(cache.store)