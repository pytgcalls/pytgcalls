import json
from aiohttp.web_request import BaseRequest
from aiohttp import web


class UpdateCallData:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _update_call_data(self, request: BaseRequest):
        params = await request.json()
        if isinstance(params, str):
            params = json.loads(params)
        for event in self.pytgcalls._on_event_update['EVENT_UPDATE_HANDLER']:
            event['callable'](params)
        return web.Response(content_type='text/plain', text='OK')
