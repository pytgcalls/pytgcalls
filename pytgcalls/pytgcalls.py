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
from .types.update_solver import UpdateSolver


class PyTgCalls(Methods, Scaffold):
    """PyTgCalls Client, the main means
    for interacting with Group Calls.

    Attributes:
        active_calls (List of :obj:`~pytgcalls.types.GroupCall`):
            Get a list of active (Playing / Paused) group calls
        calls (List of :obj:`~pytgcalls.types.GroupCall`):
            Get a list of existent group calls
        cache_peer (`InputPeer (P)`_ | `InputPeer (T)`_):
            Get current Telegram user
        ping (``int``):
            Ping of NodeJS core
        is_connected (``bool``):
            Check if is alive the NodeJS connection

    Parameters:
        app (`Client`_ | `TelegramClient`_):
            Pass the MtProto Client

        cache_duration (``int``):
            Cache duration of Full Chat query

        overload_quiet_mode (``bool``):
            Disable overload cpu messages by setting true

        multi_thread (``bool``):
            This will use NodeJS on Multi Thread mode, not
            suggested on production code (Is really buggy,
            is just an experimental mode)

    Raises:
        InvalidMtProtoClient: You set an invalid MtProto client

    """

    def __init__(
        self,
        app: Any,
        cache_duration: int = 120,
        overload_quiet_mode: bool = False,
        # BETA SUPPORT, BY DEFAULT IS DISABLED
        multi_thread: bool = False,
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
        self._wait_join_result = UpdateSolver()
        self._on_event_update = HandlersHolder()
        self._binding = Binding(
            overload_quiet_mode,
            multi_thread,
        )

        def cleanup():
            if self._async_core is not None:
                self._async_core.cancel()
        atexit.register(cleanup)
