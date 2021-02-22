import json
from aiohttp.web_request import BaseRequest
from aiohttp import web


class CustomApiUpdate:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _custom_api_update(self, request: BaseRequest):
        params = await request.json()
        if isinstance(params, str):
            params = json.loads(params)
        return web.json_response(await self.pytgcalls._on_event_update['CUSTOM_API_HANDLER'][0]['callable'](params))
