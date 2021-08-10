from aiohttp import web


class UpdateCallData:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _update_call_data(self, params: dict):
        chat_id = int(params['chat_id'])
        if params['result'] == 'PAUSED_AUDIO_STREAM':
            self._pytgcalls._set_status(chat_id, 'paused')
        elif params['result'] == 'RESUMED_AUDIO_STREAM':
            self._pytgcalls._set_status(chat_id, 'playing')
        elif params['result'] == 'JOINED_VOICE_CHAT' or \
                params['result'] == 'CHANGED_AUDIO_STREAM':
            self._pytgcalls._add_active_call(params['chat_id'])
            self._pytgcalls._add_call(chat_id)
            self._pytgcalls._set_status(chat_id, 'playing')
        elif params['result'] == 'LEFT_VOICE_CHAT' or \
                params['result'] == 'KICKED_FROM_GROUP':
            self._pytgcalls._remove_active_call(chat_id)
            self._pytgcalls._remove_call(chat_id)
        for event in self._pytgcalls._on_event_update[
            'EVENT_UPDATE_HANDLER'
        ]:
            self._pytgcalls.run_async(
                event['callable'],
                (params,),
            )
        return web.Response(content_type='text/plain', text='OK')
