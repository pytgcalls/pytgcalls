from typing import Dict
from typing import Union

from ntgcalls import NTgCalls


class Scaffold:
    _REQUIRED_PYROGRAM_VERSION = '1.2.20'
    _REQUIRED_TELETHON_VERSION = '1.24.0'
    _REQUIRED_HYDROGRAM_VERSION = '0.1.4'

    def __init__(self):
        self._app = None
        self._async_core = None
        self._is_running = None
        self._my_id = None
        self._env_checker = None
        self._cache_user_peer = None
        self._wait_result = None
        self._cache_local_peer = None
        self._on_event_update = None
        # noinspection PyTypeChecker
        self._binding: NTgCalls = None
        self._need_unmute: Dict[int, bool] = {}

    def _handle_mtproto(self):
        pass

    async def _init_mtproto(self):
        pass

    async def _resolve_chat_id(self, chat_id: Union[int, str]) -> int:
        pass

    async def get_call(self, chat_id: int):
        pass

    async def start(self):
        pass
