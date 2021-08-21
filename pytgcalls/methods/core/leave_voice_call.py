from pyrogram.raw.functions.phone import LeaveGroupCall

from ...scaffold import Scaffold


class LeaveVoiceCall(Scaffold):
    async def _leave_voice_call(
        self,
        params: dict,
    ):
        result = {
            'result': 'OK',
        }
        try:
            chat_call = await self._full_chat_cache.get_full_chat(
                int(params['chat_id']),
            )
            if chat_call is not None:
                await self._app.send(
                    LeaveGroupCall(
                        call=chat_call,
                        source=0,
                    ),
                )
        except Exception as e:
            result = {
                'result': str(e),
            }
        return result
