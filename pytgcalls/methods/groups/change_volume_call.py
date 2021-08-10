import json

import requests

from ..core import SpawnProcess


class ChangeVolume(SpawnProcess):
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def change_volume_call(self, chat_id: int, volume: int):
        volume = int(volume) if isinstance(volume, str) else volume
        js_core_state = self._pytgcalls.is_running_js_core()
        if self._pytgcalls._app is not None and\
                chat_id in self._pytgcalls._cache_user_peer:
            volume = 200 if volume > 200 else (0 if volume < 0 else volume)
            try:
                if js_core_state:
                    self._spawn_process(
                        requests.post,
                        (
                            'http://'
                            f'{self._pytgcalls._host}:'
                            f'{self._pytgcalls._port}/'
                            'request_change_volume',
                            json.dumps({
                                'chat_id': chat_id,
                                'volume': volume,
                                'session_id': self._pytgcalls._session_id,
                            }),
                        ),
                    )
                else:
                    self._pytgcalls._waiting_start_request.append([
                        self.change_volume_call,
                        (
                            chat_id,
                            volume,
                        ),
                    ])
            except Exception:
                raise Exception('Error internal: NOT_IN_GROUP')
        else:
            code_err = 'PYROGRAM_CLIENT_IS_NOT_RUNNING'
            if chat_id not in self._pytgcalls._cache_user_peer:
                code_err = 'GROUP_CALL_NOT_FOUND'
            raise Exception(f'Error internal: {code_err}')
