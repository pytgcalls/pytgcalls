from json import JSONDecodeError
from typing import Callable
from typing import Optional

from aiohttp import web
from aiohttp.web_request import Request

from ..exceptions import TooManyCustomApiDecorators


class CustomApi:
    def __init__(
        self,
        port: int = 24859,
    ):
        self._handler: Optional[Callable] = None
        self._app: web.Application = web.Application()
        self._runner: Optional[web.AppRunner] = None
        self._port = port

    def on_update_custom_api(self) -> Callable:
        if self._handler is not None:
            raise TooManyCustomApiDecorators()

        def decorator(func: Callable) -> Callable:
            self._handler = func
            return func

        return decorator

    async def start(self):
        async def on_update(request: Request):
            try:
                params = await request.json()
            except JSONDecodeError:
                return web.json_response({
                    'result': 'INVALID_JSON_FORMAT_REQUEST',
                })

            if self._handler is None:
                return web.json_response({
                    'result': 'NO_CUSTOM_API_DECORATOR',
                })

            result = await self._handler(params)
            if isinstance(result, (dict, list)):
                return web.json_response(result)
            else:
                return web.json_response({
                    'result': 'INVALID_RESPONSE',
                })

        self._app.router.add_post(
            '/',
            on_update,
        )
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, 'localhost', self._port)
        await site.start()

    async def stop(self):
        if self._runner is not None:
            await self._runner.cleanup()
