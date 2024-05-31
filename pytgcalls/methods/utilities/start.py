import asyncio
import logging

from ntgcalls import ConnectionError
from ntgcalls import ConnectionNotFound
from ntgcalls import ConnectionState
from ntgcalls import MediaState
from ntgcalls import StreamType
from ntgcalls import TelegramServerError

from ...exceptions import CallDeclined
from ...exceptions import CallDiscarded
from ...exceptions import PyTgCallsAlreadyRunning
from ...mtproto import BridgedClient
from ...pytgcalls_session import PyTgCallsSession
from ...scaffold import Scaffold
from ...types import CallData
from ...types import ChatUpdate
from ...types import GroupCallParticipant
from ...types import RawCallUpdate
from ...types import StreamAudioEnded
from ...types import StreamVideoEnded
from ...types import Update
from ...types import UpdatedGroupCallParticipant

py_logger = logging.getLogger('pytgcalls')


class Start(Scaffold):
    async def start(self):

        @self._app.on_update()
        async def update_handler(update: Update):
            chat_id = update.chat_id
            if update.chat_id in self._p2p_configs:
                p2p_config = self._p2p_configs[chat_id]
                if not p2p_config.wait_data.done():
                    if isinstance(update, RawCallUpdate):
                        if update.status & RawCallUpdate.Type.UPDATED_CALL:
                            p2p_config.wait_data.set_result(
                                update,
                            )
                    if isinstance(update, ChatUpdate) and \
                            p2p_config.outgoing:
                        if update.status & ChatUpdate.Status.DISCARDED_CALL:
                            p2p_config.wait_data.set_exception(
                                CallDeclined(
                                    chat_id,
                                ),
                            )
            if chat_id in self._wait_connect and \
                    not self._wait_connect[chat_id].done():
                if isinstance(update, ChatUpdate):
                    if update.status & ChatUpdate.Status.DISCARDED_CALL:
                        self._wait_connect[chat_id].set_exception(
                            CallDiscarded(
                                chat_id,
                            ),
                        )
            if isinstance(update, RawCallUpdate):
                if update.status & RawCallUpdate.Type.REQUESTED:
                    self._p2p_configs[chat_id] = CallData(
                        await self._app.get_dhc(),
                        self.loop,
                        update.g_a_or_b,
                    )
                    update = ChatUpdate(
                        chat_id,
                        ChatUpdate.Status.INCOMING_CALL,
                    )
            if isinstance(update, RawCallUpdate):
                if update.status & RawCallUpdate.Type.SIGNALING_DATA:
                    try:
                        await self._binding.send_signaling(
                            update.chat_id,
                            update.signaling_data,
                        )
                    except (ConnectionNotFound, ConnectionError):
                        pass
            if isinstance(update, ChatUpdate):
                if update.status & ChatUpdate.Status.LEFT_CALL:
                    await clear_call(chat_id)
            if isinstance(update, UpdatedGroupCallParticipant):
                participant = update.participant
                action = participant.action
                chat_peer = self._cache_user_peer.get(chat_id)
                if chat_peer:
                    is_self = BridgedClient.chat_id(
                        chat_peer,
                    ) == participant.user_id if chat_peer else False
                    if is_self:
                        if action == GroupCallParticipant.Action.LEFT:
                            if await clear_call(chat_id):
                                await self.propagate(
                                    ChatUpdate(
                                        chat_id,
                                        ChatUpdate.Status.KICKED,
                                    ),
                                    self,
                                )
                        if (
                            chat_id in self._need_unmute and
                            action == GroupCallParticipant.Action.UPDATED and
                            not participant.muted_by_admin
                        ):
                            try:
                                await update_status(
                                    chat_id,
                                    await self._binding.get_state(chat_id),
                                )
                            except ConnectionNotFound:
                                pass

                        if (
                            participant.muted_by_admin and
                            action != GroupCallParticipant.Action.LEFT
                        ):
                            self._need_unmute.add(chat_id)
                        else:
                            self._need_unmute.discard(chat_id)
            if not isinstance(update, RawCallUpdate):
                await self.propagate(
                    update,
                    self,
                )

        async def clear_call(chat_id) -> bool:
            res = False
            try:
                await self._binding.stop(chat_id)
                res = True
            except ConnectionNotFound:
                pass
            await clear_cache(chat_id)
            return res

        async def update_status(chat_id: int, state: MediaState):
            try:
                await self._app.set_call_status(
                    chat_id,
                    state.muted,
                    state.video_paused,
                    state.video_stopped,
                    self._cache_user_peer.get(chat_id),
                )
            except Exception as e:
                py_logger.debug(f'SetVideoCallStatus: {e}')

        async def stream_ended(chat_id: int, stream: StreamType):
            await self.propagate(
                StreamAudioEnded(
                    chat_id,
                ) if stream == StreamType.AUDIO else
                StreamVideoEnded(
                    chat_id,
                ),
                self,
            )

        async def emit_sig_data(chat_id: int, data: bytes):
            try:
                await self._app.send_signaling(
                    chat_id,
                    data,
                )
            except (ConnectionError, ConnectionNotFound):
                pass

        async def connection_changed(chat_id: int, state: ConnectionState):
            if state == ConnectionState.CONNECTING:
                return
            if chat_id in self._wait_connect:
                if state == ConnectionState.CONNECTED:
                    self._wait_connect[chat_id].set_result(None)
                else:
                    self._wait_connect[chat_id].set_exception(
                        TelegramServerError(),
                    )
                    await clear_cache(chat_id)

            if state != ConnectionState.CONNECTED:
                if chat_id > 0:
                    await self._app.discard_call(chat_id)
                await clear_cache(chat_id)

        async def clear_cache(chat_id: int):
            self._p2p_configs.pop(chat_id, None)
            self._cache_user_peer.pop(chat_id)
            self._need_unmute.discard(chat_id)

        if not self._is_running:
            self._is_running = True
            self._env_checker.check_environment()
            if not self._app.is_connected:
                await self._app.start()

            self._my_id = await self._app.get_id()
            self._cache_local_peer = await self._app.resolve_peer(
                self._my_id,
            )
            if self._app.no_updates:
                py_logger.warning(
                    f'Using {self._app.package_name.capitalize()} '
                    'client in no_updates mode is not recommended. '
                    'This mode may cause unexpected behavior or '
                    'limitations.',
                )
            else:
                self._handle_mtproto()

            self._binding.on_stream_end(
                lambda chat_id, stream: asyncio.run_coroutine_threadsafe(
                    stream_ended(chat_id, stream),
                    self.loop,
                ),
            )
            self._binding.on_upgrade(
                lambda chat_id, state: asyncio.run_coroutine_threadsafe(
                    update_status(chat_id, state),
                    self.loop,
                ),
            )
            self._binding.on_connection_change(
                lambda chat_id, state: asyncio.run_coroutine_threadsafe(
                    connection_changed(chat_id, state),
                    self.loop,
                ),
            )
            self._binding.on_signaling(
                lambda chat_id, data: asyncio.run_coroutine_threadsafe(
                    emit_sig_data(chat_id, data),
                    self.loop,
                ),
            )
            await PyTgCallsSession().start()
        else:
            raise PyTgCallsAlreadyRunning()
