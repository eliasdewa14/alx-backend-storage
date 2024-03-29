#!/usr/bin/env python3
"""Writing strings to Redis"""

from functools import wraps
from typing import Callable, Optional, Union
from uuid import uuid4
import redis


def count_calls(method: Callable) -> Callable:
    """a method that return function that increments the count for
    that key every time the method is called and
    returns the value returned by the original method.
    """

    @wraps(method)
    def wrapper(self, *args, **kwds):
        """a method that return a wrapper function
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwds)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Storing lists
    """
    @wraps(method)
    def wrapper(self, *args, **kwds):
        """a method that return a wrapper function
        """
        key = method.__qualname__
        inputs = key + ":inputs"
        outputs = key + ":outputs"
        self._redis.rpush(inputs, str(args))
        value = method(self, *args, **kwds)
        self._redis.rpush(outputs, str(value))
        return value
    return wrapper


def replay(fn: Callable):
    """a method to display the history of calls of a particular function"""
    fn_name = fn.__qualname__
    inputs = redis.Redis().lrange(fn_name + ":inputs", 0, -1)
    outputs = redis.Redis().lrange(fn_name + ":outputs", 0, -1)


class Cache():
    """Define a cache class
    """

    def __init__(self):
        """Initialize
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """method that generate a random key, store the input data in Redis
        using the random key and return the key
        """
        generate_random_key = str(uuid4())
        self._redis.set(generate_random_key, data)
        return generate_random_key

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        """method that take a key string argument and
        an optional Callable argument
        """
        if fn:
            return fn(self._redis.get(key))
        return self._redis.get(key)

    def get_str(self, key):
        """method to automatically parametrize Cache.get
        """
        data = self._redis.get(key)
        return data.decode('utf-8')

    def get_int(self, key):
        """method to automatically parametrize Cache.get
        """
        return self._redis.get(key, int)
