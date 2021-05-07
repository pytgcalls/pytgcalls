import json
import os

import requests

from ..core import SpawnProcess


class ChangeStream(SpawnProcess):
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def change_stream(self, chat_id: int, file_path: str):
        if (
            self.pytgcalls._init_js_core and
            self.pytgcalls._app is not None and
            os.path.isfile(file_path)
        ):
            self._spawn_process(
                requests.post,
                (
                    f'http://'
                    f'{self.pytgcalls._host}:'
                    f'{self.pytgcalls._port}/'
                    f'api_internal',
                    json.dumps({
                        'action': 'change_stream',
                        'chat_id': chat_id,
                        'file_path': file_path,
                        'session_id': self.pytgcalls._session_id,
                    }),
                ),
            )
        else:
            code_err = 'PYROGRAM_CLIENT_IS_NOT_RUNNING'
            if not self.pytgcalls._init_js_core:
                code_err = 'JS_CORE_NOT_RUNNING'
            if not os.path.isfile(file_path):
                code_err = 'FILE_NOT_FOUND'
            raise Exception(f'Error internal: {code_err}')
