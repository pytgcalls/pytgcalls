import json

from aiohttp import web
from aiohttp.abc import BaseRequest


class AsyncResult:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _async_result(self, request: BaseRequest):
        params = await request.json()
        if isinstance(params, str):
            params = json.loads(params)
        try:
            def_call = self.pytgcalls._async_processes[params['ID']]
            self.pytgcalls._async_processes[params['ID']] = {
                'RESULT': await def_call['CALLABLE'](*def_call['TUPLE']),
            }
        except Exception as e:
            self.pytgcalls._async_processes[params['ID']] = {
                'RESULT': e,
            }
        return web.json_response({
            'result': 'OK',
        })
