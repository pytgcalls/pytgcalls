import inspect
from functools import wraps

from .exceptions import ClientNotStarted
from .exceptions import NoMTProtoClientSet


def mtproto_required(func):
    def check_mtproto(*args, **_):
        self = args[0]
        if not self._app:
            raise NoMTProtoClientSet()

        if not self._is_running:
            raise ClientNotStarted()

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        check_mtproto(*args, **kwargs)
        return await func(*args, **kwargs)

    @wraps(func)
    def wrapper(*args, **kwargs):
        check_mtproto(*args, **kwargs)
        return func(*args, **kwargs)

    if inspect.iscoroutinefunction(func) or \
            inspect.isasyncgenfunction(func):
        return async_wrapper
    else:
        return wrapper
