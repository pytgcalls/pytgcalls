import asyncio
from asyncio import AbstractEventLoop
from typing import Any
from typing import Callable


class ToAsync:
    def __init__(self, function: Callable, *args):
        self._loop: AbstractEventLoop = asyncio.get_event_loop()
        self._function: Callable = function
        self._function_args: tuple = args

    async def _run(self):
        result: Any = await self._loop.run_in_executor(
            None,
            self._function,
            *self._function_args,
        )

        return result

    def __await__(self):
        return self._run().__await__()
