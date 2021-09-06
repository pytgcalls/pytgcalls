from asyncio.log import logger

from pytgcalls.scaffold import Scaffold


class SetVideoCallStatus(Scaffold):
    async def _set_video_call_status(
        self,
        params: dict,
    ):
        result = {
            'result': 'OK',
        }
        stopped_status = params['stopped_status'] \
            if 'stopped_status' in params else None
        paused_status = params['paused_status'] \
            if 'paused_status' in params else None
        try:
            chat_id = int(params['chat_id'])
            await self._app.set_video_call_status(
                chat_id,
                stopped_status,
                paused_status,
                self._cache_user_peer.get(chat_id),
            )
        except Exception as e:
            logger.error(f'SetVideoCallStatus: {e}')
            result = {
                'result': str(e),
            }
        return result
