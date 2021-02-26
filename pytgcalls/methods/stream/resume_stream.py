import json

import requests

from ..core import SpawnProcess


class ResumeStream(SpawnProcess):
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def resume_stream(self, chat_id: int):
        if self.pytgcalls._init_js_core and self.pytgcalls._app is not None:
            self._spawn_process(
                requests.post,
                (
                    f'http://'
                    f'{self.pytgcalls._host}:'
                    f'{self.pytgcalls._port}/'
                    f'api_internal',
                    json.dumps({
                        'action': 'resume',
                        'chat_id': chat_id,
                        'session_id': self.pytgcalls._session_id,
                    }),
                ),
            )
        else:
            code_err = 'PYROGRAM_CLIENT_IS_NOT_RUNNING'
            if not self.pytgcalls._init_js_core:
                code_err = 'JS_CORE_NOT_RUNNING'
            raise Exception(f'Error internal: {code_err}')
