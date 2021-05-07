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

        chat_id = int(params['chat_id'])

        if params['result'] == 'PAUSED_AUDIO_STREAM':
            self.pytgcalls._set_status(chat_id, 'paused')
        elif params['result'] == 'RESUMED_AUDIO_STREAM':
            self.pytgcalls._set_status(chat_id, 'playing')
        elif params['result'] == 'JOINED_VOICE_CHAT':
            self.pytgcalls._add_active_call(params['chat_id'])
            self.pytgcalls._add_call(chat_id)
            self.pytgcalls._set_status(chat_id, 'playing')
        elif params['result'] == 'LEFT_VOICE_CHAT' or \
                params['result'] == 'KICKED_FROM_GROUP':
            self.pytgcalls._remove_active_call(chat_id)
            self.pytgcalls._remove_call(chat_id)
        for event in self.pytgcalls._on_event_update[
            'EVENT_UPDATE_HANDLER'
        ]:
            self.pytgcalls.run_async(
                event['callable'],
                (params,),
            )
        return web.Response(content_type='text/plain', text='OK')
