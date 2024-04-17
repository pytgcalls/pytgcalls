from functools import wraps


def mutex(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        self = args[0]
        async with self._lock:
            return await func(*args, **kwargs)
    return async_wrapper
