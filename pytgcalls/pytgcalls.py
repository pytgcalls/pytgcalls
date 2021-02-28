from typing import Callable
from typing import Dict
from typing import List

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
        log_mode: bool = False,
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
        }
        self._my_id = 0
        self.is_running = False
        self._current_active_chats: List[int] = []
        self._current_status_chats: Dict[str, bool] = {}
        self._session_id = self._generate_session_id(20)
        self._log_mode = log_mode
        super().__init__(self)

    def run(self, before_start_callable: Callable = None):
        if self._app is not None:
            try:
                # noinspection PyBroadException
                @self._app.on_raw_update()
                async def on_close(client, update, _, data2):
                    if isinstance(update, UpdateChannel):
                        chat_id = int(f'-100{update.channel_id}')
                        if isinstance(
                                data2[update.channel_id],
                                ChannelForbidden,
                        ):
                            self.leave_group_call(
                                chat_id,
                                'kicked_from_group',
                            )
                    if isinstance(
                            update,
                            UpdateGroupCall,
                    ):
                        if isinstance(
                                update.call,
                                GroupCallDiscarded,
                        ):
                            self.leave_group_call(
                                int(f'-100{update.chat_id}'),
                                'closed_voice_chat',
                            )
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
                                    event['callable'](
                                        client, update.message,
                                    )
                        except Exception:
                            pass

                self._app.start()
                self._my_id = self._app.get_me()['id']
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
