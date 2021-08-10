from aiohttp import web
from aiohttp.web_request import BaseRequest

from ..core import env


class MultiInstanceManager:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    @staticmethod
    async def _multi_instance_manager(request: BaseRequest):
        request_path = request.path[1:]
        # noinspection PyBroadException
        try:
            params = await request.json()
        except Exception:
            return web.json_response({
                'result': 'INVALID_JSON_FORMAT_REQUEST',
            })
        if 'session_id' in params:
            instance = [
                instance for instance in env.client_instances
                if instance._session_id == params['session_id']
            ][0]
            if request_path == 'request_join_call':
                return await instance._join_voice_call(params)
            elif request_path == 'request_leave_call':
                return await instance._leave_voice_call(params)
            elif request_path == 'get_participants':
                return await instance._get_participants(params)
            elif request_path == 'ended_stream':
                return await instance._event_finish(params)
            elif request_path == 'update_request':
                return await instance._update_call_data(params)
            elif request_path == 'api_internal':
                return await instance._api_backend(params)
            elif request_path == 'request_change_volume':
                return await instance._change_volume_voice_call(params)
            elif request_path == 'async_request':
                return await instance._async_result(params)
        if request_path == 'api':
            if env.custom_api_instance is not None:
                return await env.custom_api_instance._custom_api_update(params)
            else:
                return web.json_response({
                    'result': 'NO_AVAILABLE_CUSTOM_API_CLIENTS',
                })
        return web.json_response({
            'result': 'INVALID_REQUEST',
        })
