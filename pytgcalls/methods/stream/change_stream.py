import asyncio

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
                if stream.stream_video is not None:
                    FileManager.check_file_exist(stream.stream_video.path)
                FileManager.check_file_exist(stream.stream_audio.path)
                if isinstance(stream, AudioPiped) or \
                        isinstance(stream, AudioVideoPiped):
                    await stream.check_pipe()

                async def internal_sender():
                    if not self._wait_until_run.done():
                        await self._wait_until_run
                    request = {
                        'action': 'change_stream',
                        'chat_id': chat_id,
                        'stream_audio': {
                            'path': stream.stream_audio.path,
                            'bitrate': stream.stream_audio.parameters.bitrate,
                        },
                    }
                    if stream.stream_video is not None:
                        request['stream_video'] = {
                            'path': stream.stream_video.path,
                            'width': stream.stream_video.parameters.width,
                            'height': stream.stream_video.parameters.height,
                            'framerate': stream.stream_video.parameters.frame_rate,
                        }
                    await self._binding.send(request)
                asyncio.ensure_future(internal_sender())
            else:
                raise NodeJSNotRunning()
        else:
            raise NoMtProtoClientSet()
