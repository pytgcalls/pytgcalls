import json

from aiohttp import web
from aiohttp.web_request import BaseRequest


class EventFinish:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _event_finish(self, request: BaseRequest):
        params = await request.json()
        if isinstance(params, str):
            params = json.loads(params)
        for event in self.pytgcalls._on_event_update['STREAM_END_HANDLER']:
            event['callable'](params['chat_id'])
        return web.Response(content_type='text/plain', text='OK')
