import asyncio
from typing import Callable


class Callback:
    def __init__(self, func: Callable, filters=None):
        self.func = func
        self.filters = filters


class HandlersHolder:
    def __init__(self):
        self._callbacks = []

    async def _propagate(
        self,
        update,
        client=None,
    ):
        if client:
            tasks = []
            for callback in self._callbacks:
                if not callback.filters or \
                        await callback.filters(client, update):
                    tasks.append(callback.func(client, update))
            await asyncio.gather(*tasks)
        else:
            await asyncio.gather(
                *[
                    callback.func(update)
                    for callback in self._callbacks
                ],
            )

    def add_handler(
        self,
        func: Callable,
        filters=None,
    ) -> Callable:
        self._callbacks.append(Callback(func, filters))
        return func

    def remove_handler(
        self,
        func: Callable,
    ):
        self._callbacks = [x for x in self._callbacks if x.func != func]

    def clear(self):
        """Clear all handlers to prevent memory leaks"""
        self._callbacks.clear()

    def get_handler_count(self) -> int:
        """Get number of registered handlers"""
        return len(self._callbacks)
