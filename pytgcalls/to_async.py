from asyncio import AbstractEventLoop
from typing import Callable


class ToAsync:
    def __init__(self, loop: AbstractEventLoop, function: Callable, *args):
        self._loop: AbstractEventLoop = loop
        self._function: Callable = function
        self._function_args: tuple = args

    def __await__(self):
        return self._loop.run_in_executor(
            None,
            self._function,
            *self._function_args,
        ).__await__()
