import logging
from typing import Union

from ntgcalls import ConnectionError
from ntgcalls import FileError
from ntgcalls import InvalidParams

from ...exceptions import AlreadyJoinedError
from ...exceptions import InvalidStreamMode
from ...exceptions import NoActiveGroupCall
from ...exceptions import NoMtProtoClientSet
from ...exceptions import TelegramServerError
from ...exceptions import UnMuteNeeded
from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...stream_type import StreamType
from ...to_async import ToAsync
from ...types.input_stream import InputStream
from ..utilities.stream_params import StreamParams

py_logger = logging.getLogger('pytgcalls')


class JoinGroupCall(Scaffold):
    async def join_group_call(
        self,
        chat_id: Union[int, str],
        stream: InputStream,
        invite_hash: str = None,
        join_as=None,
        stream_type: StreamType = None,
    ):
        if join_as is None:
            join_as = self._cache_local_peer
        if stream_type is None:
            stream_type = StreamType().local_stream
        if stream_type.stream_mode == 0:
            raise InvalidStreamMode()

        try:
            chat_id = int(chat_id)
        except ValueError:
            chat_id = BridgedClient.chat_id(
                await self._app.resolve_peer(chat_id),
            )
        self._cache_user_peer.put(chat_id, join_as)

        if self._app is not None:
            chat_call = await self._app.get_full_chat(
                chat_id,
            )

            if chat_call is not None:
                media_description = await StreamParams.get_stream_params(
                    stream,
                )

                try:
                    call_params: str = await ToAsync(
                        self._binding.createCall,
                        chat_id,
                        media_description,
                    )
                except FileError:
                    raise FileNotFoundError()
                except ConnectionError:
                    raise AlreadyJoinedError()

                result_params = await self._app.join_group_call(
                    chat_id,
                    call_params,
                    invite_hash,
                    media_description.video is not None,
                    self._cache_user_peer.get(chat_id),
                )

                try:
                    await ToAsync(
                        self._binding.connect,
                        chat_id,
                        result_params,
                    )
                except InvalidParams:
                    raise UnMuteNeeded()
                except Exception:
                    raise TelegramServerError()
            else:
                raise NoActiveGroupCall()
        else:
            raise NoMtProtoClientSet()
