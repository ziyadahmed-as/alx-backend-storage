#!/usr/bin/env python3
"""Web cache and access count tracker"""
import redis
import requests
from functools import wraps
from typing import Callable

# Connect to Redis
redis_client = redis.Redis()

def count_access(method: Callable) -> Callable:
    """Decorator to count how many times a URL is accessed"""
    @wraps(method)
    def wrapper(url: str) -> str:
        redis_client.incr(f"count:{url}")
        return method(url)
    return wrapper

def cache_page(method: Callable) -> Callable:
    """Decorator to cache page content in Redis for 10 seconds"""
    @wraps(method)
    def wrapper(url: str) -> str:
        cached = redis_client.get(f"cached:{url}")
        if cached:
            return cached.decode("utf-8")
        result = method(url)
        redis_client.setex(f"cached:{url}", 10, result)
        return result
    return wrapper

@count_access
@cache_page
def get_page(url: str) -> str:
    """Fetch the content of a URL, cache it, and count access"""
    response = requests.get(url)
    return response.text
