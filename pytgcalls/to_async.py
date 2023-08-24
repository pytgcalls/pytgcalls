import asyncio

from typing import Any
from asyncio import AbstractEventLoop


class ToAsync:
    def __init__(self, function: callable, *args):
        self._loop: AbstractEventLoop = asyncio.get_running_loop()
        self._function: callable = function
        self._function_args: tuple = args

    async def _run(self):
        result: Any = await self._loop.run_in_executor(
            None,
            self._function,
            *self._function_args
        )

        return result

    def __await__(self):
        return self._run().__await__()
