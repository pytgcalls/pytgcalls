import json

from aiohttp import web
from aiohttp.web_request import BaseRequest


class CustomApiUpdate:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _custom_api_update(self, request: BaseRequest):
        params = await request.json()
        if isinstance(params, str):
            params = json.loads(params)
        handler = self.pytgcalls._on_event_update['CUSTOM_API_HANDLER'][0]
        return web.json_response(await handler['callable'](params))
