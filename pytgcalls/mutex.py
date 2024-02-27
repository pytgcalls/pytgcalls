import asyncio
import logging
from functools import wraps
from inspect import signature
from typing import Optional


def mutex(func):
    sig = signature(func)

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        self = args[0]
        bound = sig.bind(*args, **kwargs)

        if 'chat_id' in bound.arguments:
            chat_id: Optional[int] = None
            try:
                chat_id = await self.resolve_chat_id(
                    bound.arguments['chat_id'],
                )
            except Exception as e:
                logging.debug(
                    'Error occurred while resolving chat_id. Reason: ' +
                    str(e),
                )
            if chat_id is not None:
                name = f'{func.__name__}_{chat_id}'
                if name not in self._lock:
                    self._lock[name] = asyncio.Lock()
                async with self._lock[name]:
                    try:
                        return await func(*args, **kwargs)
                    finally:
                        self._lock.pop(name, None)

        return await func(*args, **kwargs)
    return async_wrapper
