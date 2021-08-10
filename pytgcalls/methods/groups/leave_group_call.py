import json

import requests

from ..core import SpawnProcess


class LeaveGroupCall(SpawnProcess):
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def leave_group_call(self, chat_id: int, type_leave: str = 'requested'):
        js_core_state = self._pytgcalls.is_running_js_core()
        if self._pytgcalls._app is not None and\
                chat_id in self._pytgcalls._cache_user_peer:
            if js_core_state:
                self._spawn_process(
                    requests.post,
                    (
                        'http://'
                        f'{self._pytgcalls._host}:'
                        f'{self._pytgcalls._port}/'
                        'api_internal',
                        json.dumps({
                            'action': 'leave_call',
                            'chat_id': chat_id,
                            'session_id': self._pytgcalls._session_id,
                            'type': type_leave,
                        }),
                    ),
                )
            else:
                self._pytgcalls._waiting_start_request.append([
                    self.leave_group_call,
                    (
                        chat_id,
                        type_leave,
                    ),
                ])
        else:
            code_err = 'PYROGRAM_CLIENT_IS_NOT_RUNNING'
            if chat_id not in self._pytgcalls._cache_user_peer:
                code_err = 'GROUP_CALL_NOT_FOUND'
            raise Exception(f'Error internal: {code_err}')
