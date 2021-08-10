import socketio
from aiohttp import web


class StartWebApp:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def _start_web_app(self):
        self._pytgcalls._sio = socketio.AsyncServer(
            cors_allowed_origins=[],
            async_mode='aiohttp',
            async_handlers=True,
        )
        self._pytgcalls._app_core = web.Application()
        self._pytgcalls._sio.attach(self._pytgcalls._app_core)

        # noinspection PyProtectedMember
        @self._pytgcalls._sio.event
        async def connect(sid, environ):
            self._init_js_core = True
            self._run_waiting_requests()

        for request in self._pytgcalls._list_requests:
            self._pytgcalls._app_core.router.add_post(
                f'/{request}', self._pytgcalls._multi_instance_manager,
            )

        # noinspection PyTypeChecker
        web.run_app(
            self._pytgcalls._app_core,
            host=self._pytgcalls._host,
            port=self._pytgcalls._port,
            ssl_context=None,
            print=None,
        )
