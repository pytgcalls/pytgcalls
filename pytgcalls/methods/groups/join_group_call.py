import json
import os

import requests
from pyrogram.raw.base import InputPeer

from ..core import SpawnProcess
from ..stream.stream_type import StreamType


class JoinGroupCall(SpawnProcess):
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def join_group_call(
            self,
            chat_id: int,
            file_path: str,
            bitrate: int = 48000,
            invite_hash: str = None,
            join_as: InputPeer = None,
            stream_type: StreamType = None,
    ):
        if join_as is None:
            join_as = self._pytgcalls._cache_local_peer
        if stream_type is None:
            stream_type = StreamType().local_stream
        if stream_type.stream_mode == 0:
            raise Exception('Error internal: INVALID_STREAM_MODE')
        if os.path.getsize(file_path) == 0:
            raise Exception('Error internal: INVALID_FILE_STREAM')
        self._pytgcalls._cache_user_peer[chat_id] = join_as
        bitrate = 48000 if bitrate > 48000 else bitrate
        js_core_state = self._pytgcalls.is_running_js_core()
        if (
            self._pytgcalls._app is not None and
            os.path.isfile(file_path)
        ):
            # noinspection PyBroadException
            try:
                if js_core_state:
                    self._spawn_process(
                        requests.post,
                        (
                            'http://'
                            f'{self._pytgcalls._host}:'
                            f'{self._pytgcalls._port}/'
                            'api_internal',
                            json.dumps({
                                'action': 'join_call',
                                'chat_id': chat_id,
                                'file_path': file_path,
                                'invite_hash': invite_hash,
                                'bitrate': bitrate,
                                'buffer_long': stream_type.stream_mode,
                                'session_id': self._pytgcalls._session_id,
                            }),
                        ),
                    )
                else:
                    self._pytgcalls._waiting_start_request.append([
                        self.join_group_call,
                        (
                            chat_id,
                            file_path,
                            bitrate,
                            invite_hash,
                            join_as,
                            stream_type,
                        ),
                    ])
            except Exception as e:
                raise Exception('Error internal: UNKNOWN ->', e)
        else:
            code_err = 'PYROGRAM_CLIENT_IS_NOT_RUNNING'
            if not os.path.isfile(file_path):
                code_err = 'FILE_NOT_FOUND'
            raise Exception(f'Error internal: {code_err}')
