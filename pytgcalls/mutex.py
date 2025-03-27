from functools import wraps

from .wait_counter_lock import WaitCounterLock


def mutex(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        self = args[0]
        chat_id = await self.resolve_chat_id(args[1])
        async with self._lock:
            self._calls_lock[chat_id] = self._calls_lock.get(
                chat_id,
            ) or WaitCounterLock()
        async with self._calls_lock[chat_id]:
            result = await func(*args, **kwargs)

        async with self._lock:
            if not self._calls_lock[chat_id].waiters():
                self._calls_lock.pop(chat_id, None)
        return result
    return async_wrapper
