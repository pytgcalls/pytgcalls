import logging

from ...scaffold import Scaffold

py_logger = logging.getLogger('pytgcalls')


# TODO refactor needed
class JoinVoiceCall(Scaffold):
    async def _join_voice_call(
        self,
        params: dict,
    ):
        chat_id = int(params['chat_id'])
        try:
            return await self._app.join_group_call(
                chat_id,
                request_call,
                params['invite_hash'],
                params['have_video'],
                self._cache_user_peer.get(chat_id),
            )
        except Exception as e:
            if 'GROUPCALL_FORBIDDEN' in str(e):
                self._cache_user_peer.pop(chat_id)

            py_logger.error(f'JOIN_VOICE_CALL_ERROR -> {e}')
            return {'transport': None, 'error': str(e)}
