import asyncio
import os

from pyrogram.raw.base import InputPeer

from ...exceptions import InvalidStreamMode, PyrogramNotSet, NodeJSNotRunning, NoActiveVoiceChat
from ...scaffold import Scaffold
from ...stream_type import StreamType


class JoinGroupCall(Scaffold):
    async def join_group_call(
        self,
        chat_id: int,
        file_path: str,
        bitrate: int = 48000,
        invite_hash: str = None,
        join_as: InputPeer = None,
        stream_type: StreamType = None,
    ):
        if join_as is None:
            join_as = self._cache_local_peer
        if stream_type is None:
            stream_type = StreamType().local_stream
        if stream_type.stream_mode == 0:
            raise InvalidStreamMode()
        self._cache_user_peer.put(chat_id, join_as)
        bitrate = 48000 if bitrate > 48000 else bitrate
        if os.path.isfile(file_path):
            if self._app is not None:
                if self._binding.is_alive() or \
                        self._wait_until_run is not None:
                    chat_call = await self._full_chat_cache.get_full_chat(
                        chat_id,
                    )
                    if chat_call is not None:
                        async def internal_sender():
                            await self._wait_until_run.wait()
                            await asyncio.sleep(0.06)
                            await self._binding.send({
                                'action': 'join_call',
                                'chat_id': chat_id,
                                'file_path': file_path,
                                'invite_hash': invite_hash,
                                'bitrate': bitrate,
                                'buffer_long': stream_type.stream_mode,
                            })
                        asyncio.ensure_future(internal_sender())
                    else:
                        raise NoActiveVoiceChat()
                else:
                    raise NodeJSNotRunning()
            else:
                raise PyrogramNotSet()
        else:
            raise FileNotFoundError()
