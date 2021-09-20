import asyncio
import logging
import shlex

from ...exceptions import NodeJSNotRunning
from ...exceptions import NoMtProtoClientSet
from ...file_manager import FileManager
from ...scaffold import Scaffold
from ...types.input_stream import AudioPiped
from ...types.input_stream import AudioVideoPiped
from ...types.input_stream import InputStream
from ...types.input_stream import VideoPiped
from ...types.input_stream.audio_image_piped import AudioImagePiped

py_logger = logging.getLogger('pytgcalls')


class ChangeStream(Scaffold):
    async def change_stream(
            self,
            chat_id: int,
            stream: InputStream,
    ):
        if self._app is not None:
            if self._wait_until_run is not None:
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
                ffmpeg_parameters = ''
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
                    ffmpeg_parameters = stream.headers
                    ffmpeg_parameters += ':_cmd_:'.join(
                        shlex.split(stream.ffmpeg_parameters),
                    )

                async def internal_sender():
                    if not self._wait_until_run.done():
                        await self._wait_until_run
                    stream_audio = stream.stream_audio
                    stream_video = stream.stream_video
                    request = {
                        'action': 'change_stream',
                        'chat_id': chat_id,
                        'ffmpeg_parameters': ffmpeg_parameters,
                        'lip_sync': stream.lip_sync,
                    }
                    if stream_audio is not None:
                        request['stream_audio'] = {
                            'path': stream_audio.path,
                            'bitrate': stream_audio.parameters.bitrate,
                        }
                    if stream.stream_video is not None:
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
                        }
                    await self._binding.send(request)

                asyncio.ensure_future(internal_sender())
            else:
                raise NodeJSNotRunning()
        else:
            raise NoMtProtoClientSet()
