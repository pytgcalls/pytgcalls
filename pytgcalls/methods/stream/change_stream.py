import asyncio
import shlex

from ...exceptions import NodeJSNotRunning
from ...exceptions import NoMtProtoClientSet
from ...file_manager import FileManager
from ...scaffold import Scaffold
from ...types.input_stream import AudioPiped
from ...types.input_stream import AudioVideoPiped
from ...types.input_stream import InputStream


class ChangeStream(Scaffold):
    async def change_stream(
        self,
        chat_id: int,
        stream: InputStream,
    ):
        if self._app is not None:
            if self._wait_until_run is not None:
                headers = None
                if isinstance(stream, AudioPiped) or \
                        isinstance(stream, AudioVideoPiped):
                    headers = stream.raw_headers
                if stream.stream_video is not None:
                    await FileManager.check_file_exist(
                        stream.stream_video.path.replace('fifo://', ''),
                        headers,
                    )
                if stream.stream_audio is not None:
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
                        request['stream_video'] = {
                            'path': stream_video.path,
                            'width': stream_video.parameters.width,
                            'height': stream_video.parameters.height,
                            'framerate': stream_video.parameters.frame_rate,
                        }
                    await self._binding.send(request)
                asyncio.ensure_future(internal_sender())
            else:
                raise NodeJSNotRunning()
        else:
            raise NoMtProtoClientSet()
