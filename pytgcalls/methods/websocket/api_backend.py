import json

from aiohttp import web
from aiohttp.web_request import BaseRequest


class ApiBackend:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _api_backend(self, request: BaseRequest):
        result_json = {
            'result': 'ACCESS_DENIED',
        }
        # noinspection PyBroadException
        try:
            params = await request.json()
            if isinstance(params, str):
                params = json.loads(params)
            if params['session_id'] == self.pytgcalls._session_id:
                await self.pytgcalls._sio.emit('request', json.dumps(params))
                result_json = {
                    'result': 'ACCESS_GRANTED',
                }
                if params['action'] == 'join_call':
                    self.pytgcalls._current_active_chats.append(
                        params['chat_id'],
                    )
                elif params['action'] == 'leave_call':
                    self.pytgcalls._current_active_chats.remove(
                        params['chat_id'],
                    )
        except Exception:
            pass
        return web.json_response(result_json)
