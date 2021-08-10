from aiohttp import web


class AsyncResult:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    async def _async_result(self, params: dict):
        try:
            def_call = self._pytgcalls._async_processes[params['ID']]
            self._pytgcalls._async_processes[params['ID']] = {
                'RESULT': await def_call['CALLABLE'](*def_call['TUPLE']),
            }
        except Exception as e:
            self._pytgcalls._async_processes[params['ID']] = {
                'RESULT': e,
            }
        return web.json_response({
            'result': 'OK',
        })
