from aiohttp import web


class EventFinish:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _event_finish(self, params: dict):
        chat_id = int(params['chat_id'])
        self._pytgcalls._remove_active_call(chat_id)

        for event in self._pytgcalls._on_event_update['STREAM_END_HANDLER']:
            self._pytgcalls.run_async(
                event['callable'],
                (chat_id,),
            )
        return web.Response(content_type='text/plain', text='OK')
