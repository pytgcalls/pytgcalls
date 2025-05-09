import logging

from ntgcalls import MediaState

from ...scaffold import Scaffold

py_logger = logging.getLogger('pytgcalls')


class UpdateStatus(Scaffold):
    async def _update_status(self, chat_id: int, state: MediaState):
        try:
            await self._app.set_call_status(
                chat_id,
                state.muted,
                state.video_paused,
                state.video_stopped,
                state.presentation_paused,
                self._cache_user_peer.get(chat_id),
            )
        except Exception as e:
            py_logger.debug(f'SetVideoCallStatus: {e}')
