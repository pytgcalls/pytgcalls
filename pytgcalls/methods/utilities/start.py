import asyncio
import logging

from ntgcalls import ConnectionNotFound
from ntgcalls import MediaState
from ntgcalls import StreamType

from ...exceptions import PyTgCallsAlreadyRunning
from ...mtproto import BridgedClient
from ...pytgcalls_session import PyTgCallsSession
from ...scaffold import Scaffold
from ...to_async import ToAsync
from ...types import GroupCallParticipant
from ...types import StreamAudioEnded
from ...types import StreamVideoEnded

py_logger = logging.getLogger('pytgcalls')


class Start(Scaffold):
    async def start(self):
        loop = asyncio.get_event_loop()

        async def participants_handler(chat_id: int, participant: GroupCallParticipant, just_joined: bool, just_left: bool):
            chat_peer = self._cache_user_peer.get(chat_id)
            is_self = BridgedClient.chat_id(
                chat_peer,
            ) == participant.user_id if chat_peer else False
            if is_self:
                if chat_id in self._need_unmute and not just_joined and not just_left and not participant.muted_by_admin:
                    try:
                        await update_status(chat_id, self._binding.get_state(chat_id))
                    except ConnectionNotFound:
                        pass
                if participant.muted_by_admin:
                    self._need_unmute.add(chat_id)
                elif chat_id in self._need_unmute:
                    self._need_unmute.remove(chat_id)

        async def clear_call(chat_id: int):
            try:
                await ToAsync(self._binding.stop, chat_id)
            except ConnectionNotFound:
                pass
            self._cache_user_peer.pop(chat_id, None)
            self._need_unmute.discard(chat_id)

        def stream_upgrade(chat_id: int, state: MediaState):
            asyncio.create_task(update_status(chat_id, state))

        async def update_status(chat_id: int, state: MediaState):
            try:
                await self._app.set_call_status(chat_id, state.muted, state.video_paused, state.video_stopped, self._cache_user_peer.get(chat_id))
            except Exception as e:
                py_logger.debug(f'SetVideoCallStatus: {e}')

        async def async_stream_ended(chat_id: int, stream: StreamType):
            await self._on_event_update.propagate('STREAM_END_HANDLER', self, StreamAudioEnded(chat_id) if stream == StreamType.Audio else StreamVideoEnded(chat_id))

        if not self._is_running:
            self._is_running = True
            self._env_checker.check_environment()
            await self._init_mtproto()
            if not self._app.no_updates:
                py_logger.warning(
                    f'Using {self._app.package_name.capitalize()} client in no_updates mode is not recommended. This mode may cause unexpected behavior or limitations.',
                )
            else:
                self._handle_mtproto()

            self._binding.on_upgrade(stream_upgrade)
            self._binding.on_stream_end(
                lambda chat_id, stream: asyncio.create_task(
                async_stream_ended(chat_id, stream),
                ),
            )
            self._app.on_participants_change(participants_handler)
            self._app.on_kicked(clear_call)
            self._app.on_left_group(clear_call)
            self._app.on_closed_voice_chat(clear_call)

            await PyTgCallsSession().start()
        else:
            raise PyTgCallsAlreadyRunning()
