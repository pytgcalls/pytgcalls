import asyncio
import functools
import inspect
import threading

from .custom_api import CustomApi
from .methods import Methods


def async_to_sync(obj, name):
    function = getattr(obj, name)
    main_loop = asyncio.get_event_loop()

    async def consume_generator(coroutine):
        return [i async for i in coroutine]

    @functools.wraps(function)
    def async_to_sync_wrap(*args, **kwargs):
        coroutine = function(*args, **kwargs)

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = main_loop

        if loop.is_running():
            if threading.current_thread() is threading.main_thread():
                return coroutine
            else:
                if inspect.iscoroutine(coroutine):
                    return asyncio.run_coroutine_threadsafe(
                        coroutine,
                        loop,
                    ).result()

                if inspect.isasyncgen(coroutine):
                    return asyncio.run_coroutine_threadsafe(
                        consume_generator(coroutine),
                        loop,
                    ).result()

        if inspect.iscoroutine(coroutine):
            try:
                return loop.run_until_complete(coroutine)
            except KeyboardInterrupt:
                pass

        if inspect.isasyncgen(coroutine):
            return loop.run_until_complete(
                consume_generator(coroutine),
            )

    setattr(obj, name, async_to_sync_wrap)


def wrap(source):
    for name in dir(source):
        method = getattr(source, name)

        if not name.startswith('_'):
            if inspect.iscoroutinefunction(method) or \
                    inspect.isasyncgenfunction(method):
                async_to_sync(source, name)


# Wrap all Client's relevant methods
wrap(Methods)
wrap(CustomApi)


class ASyncer:
    pass
