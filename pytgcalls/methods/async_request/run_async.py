# noreorder
import json
import requests

from typing import Callable


class RunAsync:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def run_async(self, func: Callable, data: tuple):
        id_request = self.pytgcalls._generate_session_id(10)
        self.pytgcalls._async_processes[id_request] = {
            'CALLABLE': func,
            'TUPLE': data,
        }
        self.pytgcalls._spawn_process(
            requests.post,
            (
                'http://'
                f'{self.pytgcalls._host}:'
                f'{self.pytgcalls._port}/'
                'async_request',
                json.dumps({
                    'ID': id_request,
                }),
                60,
            ),
        )
