import json

from aiohttp import web
from aiohttp.web_request import BaseRequest
from pyrogram.raw.functions.phone import EditGroupCallParticipant


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
        chat_id = params['chatId']
        if params['sessionId'] == self.pytgcalls._session_id:
            # noinspection PyBroadException
            try:
                chat_call = (
                    await self.pytgcalls._load_full_chat(chat_id)
                ).full_chat.call
                await self.pytgcalls._app.send(
                    EditGroupCallParticipant(
                        call=chat_call,
                        participant=self.pytgcalls._cache_user_peer[chat_id],
                        muted=False,
                        volume=params['volume'] * 100,
                    ),
                )
                result_json = {'result': 'OK',}
            except Exception:
                pass
        return web.json_response(result_json)
