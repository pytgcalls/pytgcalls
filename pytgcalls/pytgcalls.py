import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from ntgcalls import NTgCalls

from .environment import Environment
from .methods import Methods
from .mtproto import MtProtoClient
from .scaffold import Scaffold
from .statictypes import statictypes
from .types import Cache


class PyTgCalls(Methods, Scaffold):
    WORKERS = min(32, (os.cpu_count() or 0) + 4)
    CACHE_DURATION = 60 * 60

    @statictypes
    def __init__(
        self,
        app: Any,
        workers: int = WORKERS,
        cache_duration: int = CACHE_DURATION,
    ):
        super().__init__()
        self._mtproto = app
        self._app = MtProtoClient(
            cache_duration,
            self._mtproto,
        )
        self._is_running = False
        self._env_checker = Environment(
            self._REQUIRED_PYROGRAM_VERSION,
            self._REQUIRED_TELETHON_VERSION,
            self._REQUIRED_HYDROGRAM_VERSION,
            self._app.package_name,
        )
        self._cache_user_peer = Cache()
        self._binding = NTgCalls()
        self.loop = asyncio.get_event_loop()
        self.workers = workers
        self._lock = asyncio.Lock()
        self.executor = ThreadPoolExecutor(
            self.workers,
            thread_name_prefix='Handler',
        )

    @property
    def cache_user_peer(self) -> Cache:
        return self._cache_user_peer

    @property
    def mtproto_client(self):
        return self._mtproto
