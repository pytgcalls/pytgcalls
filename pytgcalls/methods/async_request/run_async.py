import json
from typing import Callable

import requests


class RunAsync:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def run_async(self, func: Callable, data: tuple):
        id_request = self._pytgcalls._generate_session_id(10)
        self._pytgcalls._async_processes[id_request] = {
            'CALLABLE': func,
            'TUPLE': data,
        }
        self._pytgcalls._spawn_process(
            requests.post,
            (
                'http://'
                f'{self._pytgcalls._host}:'
                f'{self._pytgcalls._port}/'
                'async_request',
                json.dumps({
                    'ID': id_request,
                    'session_id': self._pytgcalls._session_id,
                }),
                240,
            ),
        )
