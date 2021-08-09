import socketio
from aiohttp import web


class StartWebApp:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def _start_web_app(self):
        self.pytgcalls._sio = socketio.AsyncServer(
            cors_allowed_origins=[],
            async_mode='aiohttp',
            async_handlers=True,
        )
        self.pytgcalls._app_core = web.Application()
        self.pytgcalls._sio.attach(self.pytgcalls._app_core)

        # noinspection PyProtectedMember
        @self.pytgcalls._sio.event
        async def connect(sid, environ):
            self._init_js_core = True
            self._run_waiting_requests()

        for request in self.pytgcalls._list_requests:
            self.pytgcalls._app_core.router.add_post(
                f'/{request}', self.pytgcalls._multi_instance_manager,
            )

        # noinspection PyTypeChecker
        web.run_app(
            self.pytgcalls._app_core,
            host=self.pytgcalls._host,
            port=self.pytgcalls._port,
            ssl_context=None,
            print=None,
        )
