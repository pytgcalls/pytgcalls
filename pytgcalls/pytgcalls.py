import atexit
from typing import Any

from .binding import Binding
from .environment import Environment
from .handlers import HandlersHolder
from .methods import Methods
from .mtproto import MtProtoClient
from .scaffold import Scaffold
from .types import Cache
from .types.call_holder import CallHolder


class PyTgCalls(Methods, Scaffold):
    def __init__(
        self,
        app: Any,
        cache_duration: int = 120,
    ):
        super().__init__()
        self._app = MtProtoClient(
            cache_duration,
            app,
        )
        self._is_running = False
        self._env_checker = Environment(
            self._REQUIRED_NODEJS_VERSION,
            self._REQUIRED_PYROGRAM_VERSION,
            self._REQUIRED_TELETHON_VERSION,
            self._app.client,
        )
        self._call_holder = CallHolder()
        self._cache_user_peer = Cache()
        self._on_event_update = HandlersHolder()
        self._binding = Binding()

        def cleanup():
            if self._async_core is not None:
                self._async_core.cancel()
        atexit.register(cleanup)
