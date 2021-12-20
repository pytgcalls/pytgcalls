from asyncio import Future
from typing import Optional


class Scaffold:
    _REQUIRED_NODEJS_VERSION = '15.0.0'
    _REQUIRED_PYROGRAM_VERSION = '1.2.20'
    _REQUIRED_TELETHON_VERSION = '1.24.0'

    def __init__(self):
        self._app = None
        self._async_core = None
        self._is_running = None
        self._my_id = None
        self._wait_until_run: Optional[Future] = None
        self._env_checker = None
        self._call_holder = None
        self._cache_user_peer = None
        self._wait_join_result = None
        self._cache_local_peer = None
        self._on_event_update = None
        self._binding = None

    def _handle_mtproto(self):
        pass

    async def _start_binding(self):
        pass

    async def _init_mtproto(self):
        pass

    async def _join_voice_call(self, params: dict):
        pass

    async def _leave_voice_call(self, params: dict):
        pass

    async def _stream_ended_handler(self, params: dict, is_audio: bool):
        pass

    async def _raw_update_handler(self, params: dict):
        pass

    async def _set_video_call_status(self, params: dict):
        pass

    async def start(self):
        pass
