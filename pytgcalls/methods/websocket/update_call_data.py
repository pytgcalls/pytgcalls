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
            self._set_status(params['chat_id'], 'paused')
        elif params['result'] == 'RESUMED_AUDIO_STREAM':
            self._set_status(params['chat_id'], 'playing')
        elif params['result'] == 'JOINED_VOICE_CHAT':
            self._add_active_call(params['chat_id'])
            self._add_call(params['chat_id'])
        elif params['result'] == 'LEAVED_VOICE_CHAT':
            self._rm_active_call(params['chat_id'])
            self._rm_call(params['chat_id'])
        for event in self.pytgcalls._on_event_update[
            'EVENT_UPDATE_HANDLER'
        ]:
            self.pytgcalls.run_async(
                event['callable'],
                (params,),
            )
        return web.Response(content_type='text/plain', text='OK')
