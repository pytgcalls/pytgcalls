import asyncio
import functools
import inspect
import threading

from .custom_api import CustomApi
from .media_devices import MediaDevices
from .methods import Methods
from .methods.utilities import idle as idle_module
from .mtproto import MtProtoClient


def async_to_sync(obj, name):
    function = getattr(obj, name)
    main_loop = asyncio.get_event_loop()

    def async_to_sync_gen(agen, loop, is_main_thread):
        async def a_next(a):
            try:
                return await a.__anext__(), False
            except StopAsyncIteration:
                return None, True

        while True:
            if is_main_thread:
                item, done = loop.run_until_complete(
                    a_next(agen),
                )
            else:
                item, done = asyncio.run_coroutine_threadsafe(
                    a_next(agen),
                    loop,
                ).result()
            if done:
                break
            yield item

    @functools.wraps(function)
    def async_to_sync_wrap(*args, **kwargs):
        coroutine = function(*args, **kwargs)

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if threading.current_thread() is threading.main_thread() or \
                not main_loop.is_running():
            if loop.is_running():
                return coroutine
            else:
                if inspect.iscoroutine(coroutine):
                    return loop.run_until_complete(coroutine)

                if inspect.isasyncgen(coroutine):
                    return async_to_sync_gen(
                        coroutine,
                        loop,
                        True,
                    )
        else:
            if inspect.iscoroutine(coroutine):
                if loop.is_running():
                    async def coro_wrapper():
                        return await asyncio.wrap_future(
                            asyncio.run_coroutine_threadsafe(
                                coroutine,
                                main_loop,
                            ),
                        )

                    return coro_wrapper()
                else:
                    return asyncio.run_coroutine_threadsafe(
                        coroutine,
                        main_loop,
                    ).result()

            if inspect.isasyncgen(coroutine):
                if loop.is_running():
                    return coroutine
                else:
                    return async_to_sync_gen(
                        coroutine,
                        main_loop,
                        False,
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
wrap(MtProtoClient)
wrap(MediaDevices)
async_to_sync(idle_module, 'idle')
idle = getattr(idle_module, 'idle')
