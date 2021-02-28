import json

import requests

from ..core import SpawnProcess


class LeaveGroupCall(SpawnProcess):
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def leave_group_call(self, chat_id: int, type_leave: str = 'requested'):
        if self.pytgcalls._init_js_core and self.pytgcalls._app is not None:
            self._spawn_process(
                requests.post,
                (
                    f'http://'
                    f'{self.pytgcalls._host}:'
                    f'{self.pytgcalls._port}/'
                    f'api_internal',
                    json.dumps({
                        'action': 'leave_call',
                        'chat_id': chat_id,
                        'session_id': self.pytgcalls._session_id,
                        'type': type_leave,
                    }),
                ),
            )
        else:
            code_err = 'PYROGRAM_CLIENT_IS_NOT_RUNNING'
            if not self.pytgcalls._init_js_core:
                code_err = 'JS_CORE_NOT_RUNNING'
            raise Exception(f'Error internal: {code_err}')
