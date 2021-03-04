import json
import time
from typing import Callable
import requests


class RunAsync:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def run_async(self, func: Callable, data: tuple, timeout: int = 10):
        id_request = self.pytgcalls._generate_session_id(10)
        self.pytgcalls._async_processes[id_request] = {
            'CALLABLE': func,
            'TUPLE': data
        }
        self.pytgcalls._spawn_process(
            requests.post,
            (
                f'http://'
                f'{self.pytgcalls._host}:'
                f'{self.pytgcalls._port}/'
                f'async_request',
                json.dumps({
                    'ID': id_request
                }),
                5
            )
        )
