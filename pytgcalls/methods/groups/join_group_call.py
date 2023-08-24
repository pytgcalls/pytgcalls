import logging

from typing import Union

from ntgcalls import MediaDescription, AudioDescription, InvalidParams, ConnectionError, RTMPNeeded, VideoDescription
from ...to_async import ToAsync
from ...exceptions import InvalidStreamMode, AlreadyJoinedError, TelegramServerError, RTMPStreamNeeded, UnMuteNeeded
from ...exceptions import NoActiveGroupCall
from ...exceptions import NoMtProtoClientSet
from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...stream_type import StreamType
from ...types import CaptureAudioDevice
from ...types import CaptureVideoDesktop
from ...types.input_stream import AudioPiped
from ...types.input_stream import AudioVideoPiped
from ...types.input_stream import InputStream
from ...types.input_stream import VideoPiped
from ...types.input_stream.audio_image_piped import AudioImagePiped

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
                joining to a group call (
                Telegram Server Side)
            RTMPStreamNeeded: In case you try
                to join a group call without
                a RTMP stream
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

        stream_audio = stream.stream_audio
        stream_video = stream.stream_video
        audio_description = None
        video_description = None

        raw_encoder = False
        if isinstance(
            stream,
            (AudioImagePiped, AudioPiped, AudioVideoPiped, VideoPiped, CaptureVideoDesktop, CaptureAudioDevice)
        ):
            await stream.check_pipe()
            raw_encoder = True

        if stream_audio is not None:
            audio_description = AudioDescription(
                sampleRate=stream_audio.parameters.bitrate,
                bitsPerSample=16,
                channelCount=stream_audio.parameters.channels,
                path=stream_audio.path,
            )

        if stream_video is not None:
            video_description = VideoDescription(
                width=stream_video.parameters.width,
                height=stream_video.parameters.height,
                fps=stream_video.parameters.frame_rate,
                path=stream_video.path
            )

        if self._app is not None:
            chat_call = await self._app.get_full_chat(
                chat_id,
            )

            if chat_call is not None:
                try:
                    call_params = await ToAsync(
                        self._binding.createCall(
                            chat_id,
                            MediaDescription(
                                encoder='raw' if raw_encoder else 'ffmpeg',
                                audio=audio_description,
                                video=video_description
                            )
                        )
                    )
                except ConnectionError:
                    raise AlreadyJoinedError()

                result_params = await self._app.join_group_call(
                    chat_id,
                    call_params,
                    invite_hash,
                    stream_video is not None,
                    self._cache_user_peer.get(chat_id),
                )

                try:
                    await ToAsync(
                        self._binding.connect(
                            chat_id,
                            result_params
                        )
                    )
                except InvalidParams:
                    raise UnMuteNeeded()
                except RTMPNeeded:
                    raise RTMPStreamNeeded()
                except Exception:
                    raise TelegramServerError()
            else:
                raise NoActiveGroupCall()
        else:
            raise NoMtProtoClientSet()
