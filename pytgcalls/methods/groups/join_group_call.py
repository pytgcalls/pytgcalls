import asyncio
import logging
import shlex

from ...exceptions import InvalidStreamMode
from ...exceptions import NoActiveGroupCall
from ...exceptions import NodeJSNotRunning
from ...exceptions import NoMtProtoClientSet
from ...file_manager import FileManager
from ...scaffold import Scaffold
from ...stream_type import StreamType
from ...types.input_stream import AudioPiped
from ...types.input_stream import AudioVideoPiped
from ...types.input_stream import InputStream

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
        if join_as is None:
            join_as = self._cache_local_peer
        if stream_type is None:
            stream_type = StreamType().local_stream
        if stream_type.stream_mode == 0:
            raise InvalidStreamMode()
        self._cache_user_peer.put(chat_id, join_as)
        headers = None
        if isinstance(stream, AudioPiped) or \
                isinstance(stream, AudioVideoPiped):
            headers = stream.raw_headers
        if stream.stream_video is not None:
            await FileManager.check_file_exist(
                stream.stream_video.path.replace('fifo://', ''),
                headers,
            )
        await FileManager.check_file_exist(
            stream.stream_audio.path.replace('fifo://', ''),
            headers,
        )
        ffmpeg_parameters = ''
        if isinstance(stream, AudioPiped) or \
                isinstance(stream, AudioVideoPiped):
            await stream.check_pipe()
            ffmpeg_parameters = stream.headers
            ffmpeg_parameters += ':_cmd_:'.join(
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
                    async def internal_sender():
                        request = {
                            'action': 'join_call',
                            'chat_id': chat_id,
                            'stream_audio': {
                                'path': stream_audio.path,
                                'bitrate': stream_audio.parameters.bitrate,
                            },
                            'ffmpeg_parameters': ffmpeg_parameters,
                            'invite_hash': invite_hash,
                            'buffer_long': stream_type.stream_mode,
                        }
                        if stream_video is not None:
                            video_parameters = stream_video.parameters
                            if video_parameters.frame_rate % 5 != 0:
                                py_logger.warning(
                                    'For better experience the '
                                    'video frame rate must be a multiple of 5',
                                )
                            request['stream_video'] = {
                                'path': stream_video.path,
                                'width': video_parameters.width,
                                'height': video_parameters.height,
                                'framerate': video_parameters.frame_rate,
                            }
                        await self._binding.send(request)
                    asyncio.ensure_future(internal_sender())
                else:
                    raise NoActiveGroupCall()
            else:
                raise NodeJSNotRunning()
        else:
            raise NoMtProtoClientSet()
