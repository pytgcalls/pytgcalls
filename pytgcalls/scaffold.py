from typing import List
from typing import Optional
from typing import Union

from ntgcalls import Frame as RawFrame
from ntgcalls import MediaDescription
from ntgcalls import MediaState
from ntgcalls import NetworkInfo
from ntgcalls import SegmentPartRequest
from ntgcalls import StreamDevice
from ntgcalls import StreamMode
from ntgcalls import StreamType

from .handlers import HandlersHolder
from .types import CallConfig
from .types import GroupCallConfig
from .types import Update


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
        self._call_sources = dict()
        self._wait_connect = dict()
        self._presentations = set()
        self._pending_connections = dict()

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

    async def _update_sources(self, chat_id: Union[int, str]):
        pass

    async def _join_presentation(self, chat_id: Union[int, str], join: bool):
        pass

    async def _clear_call(self, chat_id: int):
        pass

    async def _update_status(self, chat_id: int, state: MediaState):
        pass

    async def _switch_connection(self, chat_id: int):
        pass

    async def _handle_stream_ended(
        self,
        chat_id: int,
        stream_type: StreamType,
        device: StreamDevice,
    ):
        pass

    async def _emit_sig_data(self, chat_id: int, data: bytes):
        pass

    async def _request_broadcast_timestamp(
        self,
        chat_id: int,
    ):
        pass

    async def _request_broadcast_part(
        self,
        chat_id: int,
        part_request: SegmentPartRequest,
    ):
        pass

    async def _handle_stream_frame(
        self,
        chat_id: int,
        mode: StreamMode,
        device: StreamDevice,
        frames: List[RawFrame],
    ):
        pass

    async def _handle_connection_changed(
        self,
        chat_id: int,
        net_state: NetworkInfo,
    ):
        pass

    async def _handle_mtproto_updates(self, update: Update):
        pass

    async def _connect_call(
        self,
        chat_id: int,
        media_description: MediaDescription,
        config: Union[CallConfig, GroupCallConfig],
        payload: Optional[str],
    ):
        pass

    @staticmethod
    def _log_retries(r: int):
        pass

    def _clear_cache(self, chat_id: int):
        pass

    def on_update(self, filters=None):
        pass
