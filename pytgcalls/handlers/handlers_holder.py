import asyncio
from typing import Any
from typing import Callable
from typing import NamedTuple
from typing import Optional


class Callback(NamedTuple):
    func: Callable
    filters: Optional[Any]


class HandlersHolder:
    def __init__(self):
        self._callbacks = []

    async def propagate(
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
