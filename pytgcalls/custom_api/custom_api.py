from json import JSONDecodeError
from typing import Callable
from typing import Optional

from aiohttp import web
from aiohttp.web_request import BaseRequest

from ..exceptions import TooManyCustomApiDecorators


class CustomApi:
    """CustomAPI, the main means host the local http api server.

    Parameters:
        port (``int``, **optional**):
            CustomApi port to bind the API http server
    """

    def __init__(
        self,
        port: int = 24859,
    ):
        self._handler: Optional[Callable] = None
        self._app: web.Application = web.Application()
        self._runner: Optional[web.AppRunner] = None
        self._port = port

    def on_update_custom_api(self) -> Callable:
        """Decorator for handling when received http call
        to api backend

        Raises:
            TooManyCustomApiDecorators: In case you try
                to add to much decorators to a single
                CustomApi instance

        Example:
            .. code-block:: python
                :emphasize-lines: 4-5

                ...
                webserver = CustomApi(client)
                ...
                @webserver.on_update_custom_api()
                async def handler(request: dict):
                    print(update)
                    ... # Add Your Code here, switch or etc
                    return {
                        'result': 'OK',
                    }
                webserver.start()
                idle()

        """

        if self._handler is None:
            def decorator(func: Callable) -> Callable:
                if self is not None:
                    self._handler = func
                return func

            return decorator
        else:
            raise TooManyCustomApiDecorators()

    async def start(self):
        """Start the Custom Api.

        This method start the internal http webserver,
        this is helpful if you need an API interface to PyTgCalls.

        Example:
            .. code-block:: python
                :emphasize-lines: 5

                from pytgcalls import CustomApi
                from pytgcalls import idle

                webserver = CustomApi()
                webserver.start()

                idle()
        """
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
