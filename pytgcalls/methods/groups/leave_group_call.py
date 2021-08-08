import json

import requests

from ..core import SpawnProcess


class LeaveGroupCall(SpawnProcess):
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def leave_group_call(self, chat_id: int, type_leave: str = 'requested'):
        js_core_state = self.pytgcalls.is_running_js_core()
        if js_core_state and \
                self.pytgcalls._app is not None and\
                chat_id in self.pytgcalls._cache_user_peer:
            self._spawn_process(
                requests.post,
                (
                    'http://'
                    f'{self.pytgcalls._host}:'
                    f'{self.pytgcalls._port}/'
                    'api_internal',
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
            if chat_id not in self.pytgcalls._cache_user_peer:
                code_err = 'GROUP_CALL_NOT_FOUND'
            if not js_core_state:
                code_err = 'JS_CORE_NOT_RUNNING'
            raise Exception(f'Error internal: {code_err}')
