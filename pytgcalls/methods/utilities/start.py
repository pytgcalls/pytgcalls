import asyncio
from asyncio.log import logger

from ntgcalls import ConnectionNotFound
from ntgcalls import MediaState
from ntgcalls import StreamType

from ...exceptions import PyTgCallsAlreadyRunning
from ...pytgcalls_session import PyTgCallsSession
from ...scaffold import Scaffold
from pytgcalls.types import GroupCallParticipant
from pytgcalls.types import StreamAudioEnded
from pytgcalls.types import StreamVideoEnded


class Start(Scaffold):
    async def start(self):
        loop = asyncio.get_event_loop()

        @self._app.on_participants_change()
        async def participants_handler(
            chat_id: int,
            participant: GroupCallParticipant,
            just_joined: bool,
            just_left: bool,
        ):
            if chat_id in self._need_unmute:
                need_unmute = self._need_unmute[chat_id]
                if not just_joined and \
                        not just_left and \
                        need_unmute and \
                        not participant.muted_by_admin:
                    try:
                        await update_status(
                            chat_id,
                            self._binding.get_state(chat_id),
                        )
                    except ConnectionNotFound:
                        pass
                self._need_unmute[chat_id] = participant.muted_by_admin

        def stream_upgrade(chat_id: int, state: MediaState):
            asyncio.run_coroutine_threadsafe(
                update_status(chat_id, state), loop,
            )

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
                logger.error(f'SetVideoCallStatus: {e}')

        def stream_ended(chat_id: int, stream: StreamType):
            async def async_stream_ended():
                await self._on_event_update.propagate(
                    'STREAM_END_HANDLER',
                    self,
                    StreamAudioEnded(
                        chat_id,
                    ) if stream == stream.Audio else StreamVideoEnded(chat_id),
                )

            asyncio.run_coroutine_threadsafe(async_stream_ended(), loop)

        if not self._is_running:
            self._is_running = True
            self._env_checker.check_environment()
            await self._init_mtproto()
            self._handle_mtproto()

            self._binding.on_stream_end(stream_ended)
            self._binding.on_upgrade(stream_upgrade)
            await PyTgCallsSession().start()
        else:
            raise PyTgCallsAlreadyRunning()
