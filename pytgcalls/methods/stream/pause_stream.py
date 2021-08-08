import json

import requests

from ..core import SpawnProcess


class PauseStream(SpawnProcess):
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def pause_stream(self, chat_id: int):
        js_core_state = self.pytgcalls.is_running_js_core()
        if js_core_state and self.pytgcalls._app is not None:
            self._spawn_process(
                requests.post,
                (
                    'http://'
                    f'{self.pytgcalls._host}:'
                    f'{self.pytgcalls._port}/'
                    'api_internal',
                    json.dumps({
                        'action': 'pause',
                        'chat_id': chat_id,
                        'session_id': self.pytgcalls._session_id,
                    }),
                ),
            )
        else:
            code_err = 'PYROGRAM_CLIENT_IS_NOT_RUNNING'
            if not js_core_state:
                code_err = 'JS_CORE_NOT_RUNNING'
            raise Exception(f'Error internal: {code_err}')
