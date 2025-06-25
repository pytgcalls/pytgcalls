from functools import wraps


def mutex(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        self = args[0]
        chat_id = await self.resolve_chat_id(
            args[1] if len(args) > 1 else kwargs['chat_id'],
        )
        async with await self._chat_lock.acquire(chat_id):
            return await func(*args, **kwargs)
    return async_wrapper
