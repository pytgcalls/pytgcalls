from functools import wraps

from .exceptions import ClientNotStarted
from .exceptions import MTProtoClientNotConnected
from .exceptions import NoMTProtoClientSet


def mtproto_required(func):
    def check_mtproto(*args):
        self = args[0]
        if not self._app:
            raise NoMTProtoClientSet()

        if not self._is_running:
            raise ClientNotStarted()

        if not self._app.is_connected:
            raise MTProtoClientNotConnected()

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        check_mtproto(*args)
        return await func(*args, **kwargs)

    return async_wrapper
