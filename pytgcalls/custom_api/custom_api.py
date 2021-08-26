from json import JSONDecodeError
from typing import Callable
from typing import Optional

from aiohttp import web
from aiohttp.web_request import BaseRequest

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
        if self._handler is None:
            def decorator(func: Callable) -> Callable:
                if self is not None:
                    self._handler = func
                return func

            return decorator
        else:
            raise TooManyCustomApiDecorators()

    async def start(self):
        async def on_update(request: BaseRequest):
            try:
                params = await request.json()
            except JSONDecodeError:
                return web.json_response({
                    'result': 'INVALID_JSON_FORMAT_REQUEST',
                })
            if self._handler is not None:
                result = await self._handler(params)
                if isinstance(result, dict) or \
                        isinstance(result, list):
                    return web.json_response(result)
                else:
                    return web.json_response({
                        'result': 'INVALID_RESPONSE',
                    })
            else:
                return web.json_response({
                    'result': 'NO_CUSTOM_API_DECORATOR',
                })

        self._app.router.add_post(
            '/',
            on_update,
        )
        runner = web.AppRunner(self._app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self._port)
        await site.start()
