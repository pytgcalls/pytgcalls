from aiohttp import web


class CustomApiUpdate:
    def __init__(self, custom_api):
        self._custom_api = custom_api

    # noinspection PyProtectedMember
    async def _custom_api_update(self, params: dict):
        handler = self._custom_api._custom_api_handler
        if handler is not None:
            return web.json_response(await handler(params))
        else:
            return web.json_response({
                'result': 'NO_AVAILABLE_CUSTOM_API_DECORATOR',
            })
