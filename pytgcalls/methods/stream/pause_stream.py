import json

import requests

from ..core import SpawnProcess


class PauseStream(SpawnProcess):
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def pause_stream(self, chat_id: int):
        js_core_state = self._pytgcalls.is_running_js_core()
        if self._pytgcalls._app is not None:
            if js_core_state:
                self._spawn_process(
                    requests.post,
                    (
                        'http://'
                        f'{self._pytgcalls._host}:'
                        f'{self._pytgcalls._port}/'
                        'api_internal',
                        json.dumps({
                            'action': 'pause',
                            'chat_id': chat_id,
                            'session_id': self._pytgcalls._session_id,
                        }),
                    ),
                )
            else:
                self._pytgcalls._waiting_start_request.append([
                    self.pause_stream,
                    (
                        chat_id,
                    ),
                ])
        else:
            code_err = 'PYROGRAM_CLIENT_IS_NOT_RUNNING'
            raise Exception(f'Error internal: {code_err}')
