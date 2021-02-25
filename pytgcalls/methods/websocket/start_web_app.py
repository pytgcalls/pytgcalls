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

        @self.pytgcalls._sio.event
        async def connect(sid, environ):
            self._init_js_core = True

        self.pytgcalls._app_core.router.add_post(
            '/request_join_call', self.pytgcalls._join_voice_call,
        )
        self.pytgcalls._app_core.router.add_post(
            '/request_leave_call', self.pytgcalls._leave_voice_call,
        )
        self.pytgcalls._app_core.router.add_post(
            '/get_participants', self.pytgcalls._get_participants,
        )
        self.pytgcalls._app_core.router.add_post(
            '/ended_stream', self.pytgcalls._event_finish,
        )
        self.pytgcalls._app_core.router.add_post(
            '/update_request', self.pytgcalls._update_call_data,
        )
        self.pytgcalls._app_core.router.add_post(
            '/api_internal', self.pytgcalls._api_backend,
        )
        self.pytgcalls._app_core.router.add_post(
            '/request_change_volume', self.pytgcalls._change_volume_voice_call,
        )
        if len(self.pytgcalls._on_event_update['CUSTOM_API_HANDLER']) > 0:
            self.pytgcalls._app_core.router.add_post(
                '/api', self.pytgcalls._custom_api_update,
            )
        # noinspection PyTypeChecker
        web.run_app(
            self.pytgcalls._app_core,
            host=self.pytgcalls._host,
            port=self.pytgcalls._port,
            ssl_context=None,
            print=None,
        )
