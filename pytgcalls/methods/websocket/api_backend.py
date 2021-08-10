from ..core import env
import json

from aiohttp import web
from aiohttp.web_request import BaseRequest


class ApiBackend:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    @staticmethod
    async def _api_backend(params: dict):
        instances = [
            instance for instance in env.client_instances
            if instance._init_js_core
        ]
        if len(instances) > 0:
            await instances[0]._sio.emit('request', json.dumps(params))
            return web.json_response({
                'result': 'ACCESS_GRANTED',
            })
        else:
            return web.json_response({
                'result': 'ACCESS_DENIED',
            })
