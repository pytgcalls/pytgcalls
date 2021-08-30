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
            await self._app.leave_group_call(
                int(params['chat_id']),
            )
        except Exception as e:
            result = {
                'result': str(e),
            }
        return result
