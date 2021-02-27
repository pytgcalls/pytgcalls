import json

from aiohttp import web
from aiohttp.web_request import BaseRequest


class UpdateCallData:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _update_call_data(self, request: BaseRequest):
        params = await request.json()
        if isinstance(params, str):
            params = json.loads(params)
        if params['result'] == 'PAUSED_AUDIO_STREAM':
            self.pytgcalls._current_status_chats[
                int(params['chat_id'])
            ] = False
        elif params['result'] == 'RESUMED_AUDIO_STREAM' or \
                params['result'] == 'JOINED_VOICE_CHAT':
            self.pytgcalls._current_status_chats[
                int(params['chat_id'])
            ] = True
        elif params['result'] == 'LEAVED_VOICE_CHAT':
            del self.pytgcalls._current_status_chats[
                int(params['chat_id'])
            ]
        for event in self.pytgcalls._on_event_update[
            'EVENT_UPDATE_HANDLER'
        ]:
            event['callable'](params)
        return web.Response(content_type='text/plain', text='OK')
