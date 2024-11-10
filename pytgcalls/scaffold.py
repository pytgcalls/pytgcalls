from typing import Union

from .handlers import HandlersHolder


class Scaffold(HandlersHolder):
    _REQUIRED_PYROGRAM_VERSION = '1.2.20'
    _REQUIRED_TELETHON_VERSION = '1.24.0'
    _REQUIRED_HYDROGRAM_VERSION = '0.1.4'

    def __init__(self):
        super().__init__()
        self._app = None
        self._is_running = None
        self._my_id = None
        self._env_checker = None
        self._cache_user_peer = None
        self._cache_local_peer = None
        self._handlers = None
        # noinspection PyTypeChecker
        self._binding = None
        self.loop = None
        self._need_unmute = set()
        self._p2p_configs = dict()
        self._videos_id = dict()
        self._presentations_id = dict()
        self._wait_connect = dict()
        self._presentations = set()

    def _handle_mtproto(self):
        pass

    async def _init_mtproto(self):
        pass

    async def resolve_chat_id(self, chat_id: Union[int, str]):
        pass

    async def start(self):
        pass

    async def play(self, chat_id: Union[int, str], stream=None, config=None):
        pass

    def on_update(self, filters=None):
        pass
