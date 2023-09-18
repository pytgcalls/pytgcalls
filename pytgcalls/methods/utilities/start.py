import asyncio
from asyncio.log import logger

from ntgcalls import MediaState
from ntgcalls import StreamType

from ...exceptions import PyTgCallsAlreadyRunning
from ...pytgcalls_session import PyTgCallsSession
from ...scaffold import Scaffold
from pytgcalls.types import StreamAudioEnded
from pytgcalls.types import StreamVideoEnded


class Start(Scaffold):
    async def start(self):
        loop = asyncio.get_event_loop()

        def stream_upgrade(chat_id: int, state: MediaState):
            async def async_upgrade():
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

            asyncio.run_coroutine_threadsafe(async_upgrade(), loop)

        def stream_ended(chat_id: int, stream: StreamType):
            async def async_stream_ended():
                await self._on_event_update.propagate(
                    'STREAM_END_HANDLER',
                    self,
                    StreamAudioEnded(
                        chat_id,
                    ) if stream.Audio else StreamVideoEnded(chat_id),
                )

            asyncio.run_coroutine_threadsafe(async_stream_ended(), loop)

        if not self._is_running:
            self._is_running = True
            self._env_checker.check_environment()
            await self._init_mtproto()
            self._handle_mtproto()

            self._binding.onStreamEnd(stream_ended)
            self._binding.onUpgrade(stream_upgrade)
            await PyTgCallsSession().start()
        else:
            raise PyTgCallsAlreadyRunning()
