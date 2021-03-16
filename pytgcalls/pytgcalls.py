import os
from typing import Callable
from typing import Dict
from typing import List

from pyrogram import __version__
from pyrogram import Client
from pyrogram.raw.types import ChannelForbidden
from pyrogram.raw.types import GroupCallDiscarded
from pyrogram.raw.types import MessageActionInviteToGroupCall
from pyrogram.raw.types import UpdateChannel
from pyrogram.raw.types import UpdateGroupCall
from pyrogram.raw.types import UpdateNewChannelMessage

from .methods import Methods


class PyTgCalls(Methods):
    def __init__(
        self,
        app: Client,
        port: int = 24859,
        log_mode: int = 0,
    ):
        self._app = app
        self._app_core = None
        self._sio = None
        self._host = '127.0.0.1'
        self._port = port
        self._init_js_core = False
        self._on_event_update: Dict[str, list] = {
            'EVENT_UPDATE_HANDLER': [],
            'STREAM_END_HANDLER': [],
            'CUSTOM_API_HANDLER': [],
            'GROUP_CALL_HANDLER': [],
            'KICK_HANDLER': [],
            'CLOSED_HANDLER': [],
        }
        self._my_id = 0
        self.is_running = False
        self._calls: List[int] = []
        self._active_calls: Dict[int, str] = {}
        self._async_processes: Dict[str, Dict] = {}
        self._session_id = self._generate_session_id(20)
        self._log_mode = log_mode
        self._cache_user_peer: Dict[int, Dict] = {}
        self._cache_full_chat: Dict[int, Dict] = {}
        self._cache_local_peer = None
        super().__init__(self)

    @staticmethod
    def verbose_mode():
        return 1

    @property
    def ultra_verbose_mode(self):
        return 2

    @staticmethod
    def get_version(package_check):
        result_cmd = os.popen(f'{package_check} -v').read()
        result_cmd = result_cmd.replace('v', '')
        if len(result_cmd) == 0:
            return {
                'version_int': 0,
                'version': '0',
            }
        return {
            'version_int': int(result_cmd.split('.')[0]),
            'version': result_cmd,
        }

    def run(self, before_start_callable: Callable = None):
        if self._app is not None:
            node_result = self.get_version('node')
            if node_result['version_int'] == 0:
                raise Exception('Please install node (15.+)')
            if node_result['version_int'] < 15:
                raise Exception(
                    'Needed node 15.+, '
                    'actually installed is '
                    f"{node_result['version']}",
                )
            if int(__version__.split('.')[2]) < 13 and \
                    int(__version__.split('.')[1]) == 1 and \
                    int(__version__.split('.')[0]) == 1:
                raise Exception(
                    'Needed pyrogram 1.1.13+, '
                    'actually installed is '
                    f'{__version__}',
                )
            try:
                # noinspection PyBroadException
                @self._app.on_raw_update()
                async def on_close(client, update, _, data2):
                    if isinstance(update, UpdateChannel):
                        chat_id = int(f'-100{update.channel_id}')
                        if len(data2) > 0:
                            if isinstance(
                                data2[update.channel_id],
                                ChannelForbidden,
                            ):
                                for event in self._on_event_update[
                                    'KICK_HANDLER'
                                ]:
                                    await event['callable'](
                                        chat_id,
                                    )
                                # noinspection PyBroadException
                                try:
                                    self.leave_group_call(
                                        chat_id,
                                        'kicked_from_group',
                                    )
                                except Exception:
                                    pass
                                try:
                                    del self._cache_user_peer[chat_id]
                                except Exception:
                                    pass
                    if isinstance(
                            update,
                            UpdateGroupCall,
                    ):
                        if isinstance(
                                update.call,
                                GroupCallDiscarded,
                        ):
                            chat_id = int(f'-100{update.chat_id}')
                            for event in self._on_event_update[
                                'CLOSED_HANDLER'
                            ]:
                                await event['callable'](
                                    chat_id,
                                )
                            # noinspection PyBroadException
                            try:
                                self.leave_group_call(
                                    chat_id,
                                    'closed_voice_chat',
                                )
                            except Exception:
                                pass
                            try:
                                del self._cache_user_peer[chat_id]
                            except Exception:
                                pass
                    if isinstance(
                            update,
                            UpdateNewChannelMessage,
                    ):
                        try:
                            if isinstance(
                                    update.message.action,
                                    MessageActionInviteToGroupCall,
                            ):
                                for event in self._on_event_update[
                                    'GROUP_CALL_HANDLER'
                                ]:
                                    await event['callable'](
                                        client, update.message,
                                    )
                        except Exception:
                            pass
                self._app.start()
                self._my_id = self._app.get_me()['id']  # noqa
                self._cache_local_peer = self._app.resolve_peer(
                    self._my_id,
                )
                if before_start_callable is not None:
                    # noinspection PyBroadException
                    try:
                        result = before_start_callable(self._my_id)
                        if isinstance(result, bool):
                            if not result:
                                return
                    except Exception:
                        pass
                self._spawn_process(
                    self._run_js,
                    (
                        f'{__file__.replace("pytgcalls.py", "")}js/core.js',
                        f'port={self._port} log_mode={self._log_mode}',
                    ),
                )
            except KeyboardInterrupt:
                pass
            self._start_web_app()
            self.is_running = True
        else:
            raise Exception('NEED_PYROGRAM_CLIENT')
        return self

    def _add_handler(self, type_event: str, func):
        self._on_event_update[type_event].append(func)
