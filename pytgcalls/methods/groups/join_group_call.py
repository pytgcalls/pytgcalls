import logging

from typing import Union

from ntgcalls import InvalidParams, ConnectionError, FileError
from ..utilities.stream_params import StreamParams
from ...to_async import ToAsync
from ...exceptions import InvalidStreamMode, AlreadyJoinedError, TelegramServerError, UnMuteNeeded
from ...exceptions import NoActiveGroupCall
from ...exceptions import NoMtProtoClientSet
from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...stream_type import StreamType
from ...types.input_stream import InputStream

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
        """Join a group call to stream a file

        This method allow to stream a file to Telegram
        Group Calls

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier of the target chat.
                Can be a direct id (int) or a username (str)
            stream (:obj:`~pytgcalls.types.InputStream()`):
                Input Streams descriptor, can be used also
                :obj:`~pytgcalls.types.AudioPiped()`,
                :obj:`~pytgcalls.types.AudioImagePiped()`,
                :obj:`~pytgcalls.types.AudioVideoPiped()` or
                :obj:`~pytgcalls.types.VideoPiped()`
            invite_hash (``str``, **optional**):
                Unique identifier for the invite in a group call
                in form of a t.me link
            join_as (`InputPeer (P)`_ | `InputPeer (T)`_, **optional**):
                InputPeer of join as channel or profile
            stream_type (:obj:`~pytgcalls.StreamType`, **optional**)
                The type of Stream

        Raises:
            NoMtProtoClientSet: In case you try
                to call this method without any MtProto client
            NoActiveGroupCall: In case you try
                to edit a not started group call
            FileNotFoundError: In case you try
                a non-existent file #TODO
            InvalidStreamMode: In case you try
                to set a void stream mode
            FFmpegNotInstalled: In case you try
                to use the Piped input stream, and
                you don't have ffmpeg installed #TODO
            NoAudioSourceFound: In case you try
                to play an audio file from a file
                without the sound #TODO
            NoVideoSourceFound: In case you try
                to play a video file from a file
                without the video #TODO
            InvalidVideoProportion: In case you try
                to play a video without correct
                proportions #TODO
            AlreadyJoinedError: In case you try
                to join in already joined group
                call
            TelegramServerError: Error occurred when
                joining a group call (
                Telegram Server Side)
            UnMuteNeeded: In case you try
                to play on a muted group call

        Example:
            .. code-block:: python
                :emphasize-lines: 10-15

                from pytgcalls import Client
                from pytgcalls import idle
                ...

                app = PyTgCalls(client)
                app.start()

                ...  # Call API methods

                app.join_group_call(
                    -1001185324811,
                    AudioPiped(
                        'test.mp4',
                    )
                )

                idle()
        """
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
                media_description = await StreamParams.get_stream_params(stream)

                try:
                    call_params = await ToAsync(
                        self._binding.createCall,
                        chat_id,
                        media_description
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
                        result_params
                    )
                except InvalidParams:
                    raise UnMuteNeeded()
                except Exception:
                    raise TelegramServerError()
            else:
                raise NoActiveGroupCall()
        else:
            raise NoMtProtoClientSet()
