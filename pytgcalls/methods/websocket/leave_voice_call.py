import json

from aiohttp import web
from pyrogram.raw.functions.phone import LeaveGroupCall


class LeaveVoiceCall:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _leave_voice_call(self, params: dict):
        result = {
            'result': 'OK',
        }
        if isinstance(params, str):
            params = json.loads(params)
        try:
            # noinspection PyBroadException
            chat_call = await self._pytgcalls._load_chat_call(
                int(params['chat_id']),
            )
            if chat_call is not None:
                # noinspection PyBroadException
                await self._pytgcalls._app.send(
                    LeaveGroupCall(
                        call=chat_call,
                        source=0,
                    ),
                )
        except Exception as e:
            result = {
                'result': str(e),
            }
        return web.json_response(result)
