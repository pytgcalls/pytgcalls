import asyncio
from asyncio.log import logger

from ntgcalls import MediaState

from ...exceptions import PyTgCallsAlreadyRunning
from ...pytgcalls_session import PyTgCallsSession
from ...scaffold import Scaffold


class Start(Scaffold):
    async def start(self):
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

            loop = asyncio.get_event_loop()
            loop.run_until_complete(async_upgrade())

        if not self._is_running:
            self._is_running = True
            self._env_checker.check_environment()
            await self._init_mtproto()
            self._handle_mtproto()

            self._binding.onStreamEnd(self._stream_ended_handler)
            self._binding.onUpgrade(stream_upgrade)
            await PyTgCallsSession().start()
        else:
            raise PyTgCallsAlreadyRunning()
