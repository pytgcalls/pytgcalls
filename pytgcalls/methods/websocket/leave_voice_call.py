import json

from aiohttp import web
from aiohttp.web_request import BaseRequest
from pyrogram.raw.functions.phone import LeaveGroupCall


class LeaveVoiceCall:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _leave_voice_call(self, request: BaseRequest):
        params = await request.json()
        result = {
            'result': 'OK',
        }
        if isinstance(params, str):
            params = json.loads(params)
        try:
            chat_call = (
                await self.pytgcalls._load_full_chat(int(params['chat_id']))
            ).full_chat.call
            if chat_call is not None:
                # noinspection PyBroadException
                await self.pytgcalls._app.send(
                    LeaveGroupCall(
                        call=chat_call,
                        source=0,
                    ),
                )
        except Exception as e:
            result = {
                'result': str(e),
            }
            pass
        return web.json_response(result)
