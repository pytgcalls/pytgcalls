import json

from aiohttp import web
from aiohttp.web_request import BaseRequest
from pyrogram.raw.functions.phone import EditGroupCallMember
from pyrogram.raw.types import InputUser


class ChangeVolumeVoiceCall:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _change_volume_voice_call(self, request: BaseRequest):
        result_json = {
            'result': 'ACCESS_DENIED',
        }
        params = await request.json()
        if isinstance(params, str):
            params = json.loads(params)
        if params['session_id'] == self.pytgcalls._session_id:
            # noinspection PyBroadException
            try:
                chat_call = (
                    await self.pytgcalls._load_full_chat(
                        params['chat_id'],
                    )
                ).full_chat.call
                await self.pytgcalls._app.send(
                    EditGroupCallMember(
                        call=chat_call,
                        user_id=InputUser(
                            user_id=self.pytgcalls.get_cache_id(),
                            access_hash=0,
                        ),
                        muted=False,
                        volume=params['volume'] * 100,
                    ),
                )
                result_json = {
                    'result': 'OK',
                }
            except Exception:
                pass
        return web.json_response(result_json)
