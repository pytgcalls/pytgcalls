import asyncio
import logging
import shlex

from ...exceptions import AlreadyJoinedError
from ...exceptions import InvalidStreamMode
from ...exceptions import NoActiveGroupCall
from ...exceptions import NodeJSNotRunning
from ...exceptions import NoMtProtoClientSet
from ...exceptions import TelegramServerError
from ...file_manager import FileManager
from ...scaffold import Scaffold
from ...stream_type import StreamType
from ...types import AlreadyJoined
from ...types import ErrorDuringJoin
from ...types.input_stream import AudioPiped
from ...types.input_stream import AudioVideoPiped
from ...types.input_stream import InputStream
from ...types.input_stream import VideoPiped
from ...types.input_stream.audio_image_piped import AudioImagePiped
from ...types.session import Session

py_logger = logging.getLogger('pytgcalls')


class JoinGroupCall(Scaffold):
    async def join_group_call(
        self,
        chat_id: int,
        stream: InputStream,
        invite_hash: str = None,
        join_as=None,
        stream_type: StreamType = None,
    ):
        """Join a group call to stream a file

        This method allow to stream a file to Telegram
        Group Calls

        Parameters:
            chat_id (``int``):
                Unique identifier (int) of the target chat.
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
            NodeJSNotRunning: In case you try
                to call this method without do
                :meth:`~pytgcalls.PyTgCalls.start` before
            NoActiveGroupCall: In case you try
                to edit a not started group call
            FileNotFoundError: In case you try
                a non existent file
            InvalidStreamMode: In case you try
                to set a void stream mode
            FFmpegNotInstalled: In case you try
                to use the Piped input stream and
                you don't have ffmpeg installed
            NoAudioSourceFound: In case you try
                to play an audio file from a file
                without the sound
            NoVideoSourceFound: In case you try
                to play an video file from a file
                without the video
            InvalidVideoProportion: In case you try
                to play an video without correct
                proportions
            AlreadyJoinedError: In case you try
                to join in already joined group
                call
            TelegramServerError: Error occurred when
                joining to a group call (
                Telegram Server Side)

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
        self._cache_user_peer.put(chat_id, join_as)
        headers = None
        if isinstance(
            stream,
            AudioImagePiped,
        ) or isinstance(
            stream,
            AudioPiped,
        ) or isinstance(
            stream,
            AudioVideoPiped,
        ) or isinstance(
            stream,
            VideoPiped,
        ):
            headers = stream.raw_headers
        if stream.stream_video is not None:
            await FileManager.check_file_exist(
                stream.stream_video.path.replace(
                    'fifo://',
                    '',
                ).replace(
                    'image:',
                    '',
                ),
                headers,
            )
        if stream.stream_audio is not None:
            await FileManager.check_file_exist(
                stream.stream_audio.path.replace(
                    'fifo://',
                    '',
                ).replace(
                    'image:',
                    '',
                ),
                headers,
            )
        audio_f_parameters = ''
        video_f_parameters = ''
        if isinstance(
            stream,
            AudioImagePiped,
        ) or isinstance(
            stream,
            AudioPiped,
        ) or isinstance(
            stream,
            AudioVideoPiped,
        ) or isinstance(
            stream,
            VideoPiped,
        ):
            await stream.check_pipe()
            if stream.stream_audio:
                if stream.stream_audio.header_enabled:
                    audio_f_parameters = stream.headers
            audio_f_parameters += ':_cmd_:'.join(
                shlex.split(stream.ffmpeg_parameters),
            )
            if stream.stream_video:
                if stream.stream_video.header_enabled:
                    video_f_parameters = stream.headers
            video_f_parameters += ':_cmd_:'.join(
                shlex.split(stream.ffmpeg_parameters),
            )
        if self._app is not None:
            if self._wait_until_run is not None:
                if not self._wait_until_run.done():
                    await self._wait_until_run
                chat_call = await self._app.get_full_chat(
                    chat_id,
                )
                stream_audio = stream.stream_audio
                stream_video = stream.stream_video
                if chat_call is not None:
                    solver_id = Session.generate_session_id(24)

                    async def internal_sender():
                        request = {
                            'action': 'join_call',
                            'chat_id': chat_id,
                            'invite_hash': invite_hash,
                            'buffer_long': stream_type.stream_mode,
                            'lip_sync': stream.lip_sync,
                            'solver_id': solver_id,
                        }
                        if stream_audio is not None:
                            request['stream_audio'] = {
                                'path': stream_audio.path,
                                'bitrate': stream_audio.parameters.bitrate,
                                'ffmpeg_parameters': audio_f_parameters,
                            }
                        if stream_video is not None:
                            video_parameters = stream_video.parameters
                            if video_parameters.frame_rate % 5 != 0 and \
                                    not isinstance(stream, AudioImagePiped):
                                py_logger.warning(
                                    'For better experience the '
                                    'video frame rate must be a multiple of 5',
                                )
                            request['stream_video'] = {
                                'path': stream_video.path,
                                'width': video_parameters.width,
                                'height': video_parameters.height,
                                'framerate': video_parameters.frame_rate,
                                'ffmpeg_parameters': video_f_parameters,
                            }
                        await self._binding.send(request)
                    asyncio.ensure_future(internal_sender())
                    result = await self._wait_join_result.wait_future_update(
                        solver_id,
                    )
                    if isinstance(result, AlreadyJoined):
                        raise AlreadyJoinedError()
                    elif isinstance(result, ErrorDuringJoin):
                        raise TelegramServerError()
                else:
                    raise NoActiveGroupCall()
            else:
                raise NodeJSNotRunning()
        else:
            raise NoMtProtoClientSet()
