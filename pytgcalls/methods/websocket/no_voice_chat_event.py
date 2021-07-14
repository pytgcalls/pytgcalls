import json

from aiohttp import web
from aiohttp.web_request import BaseRequest


class NoVoiceChatEvent:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _no_voice_chat_event(self, request: BaseRequest):
        params = await request.json()
        if isinstance(params, str):
            params = json.loads(params)

        chat_id = int(params['chat_id'])

        for event in self.pytgcalls._on_event_update['NO_VOICE_CHAT_HANDLER']:
            self.pytgcalls.run_async(
                event['callable'],
                (chat_id,),
            )
        return web.Response(content_type='text/plain', text='OK')
