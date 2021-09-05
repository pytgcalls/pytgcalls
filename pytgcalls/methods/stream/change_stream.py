import asyncio

from ...exceptions import NodeJSNotRunning
from ...exceptions import NoMtProtoClientSet
from ...file_manager import FileManager
from ...scaffold import Scaffold
from ...types.input_stream import InputAudioStream
from ...types.input_stream import InputVideoStream


class ChangeStream(Scaffold):
    async def change_stream(
        self,
        chat_id: int,
        stream_audio: InputAudioStream,
        stream_video: InputVideoStream = None,
    ):
        if self._app is not None:
            if self._wait_until_run is not None:
                if stream_video is not None:
                    FileManager.check_file_exist(stream_video.path)
                FileManager.check_file_exist(stream_audio.path)

                async def internal_sender():
                    if not self._wait_until_run.done():
                        await self._wait_until_run
                    request = {
                        'action': 'change_stream',
                        'chat_id': chat_id,
                        'stream_audio': {
                            'path': stream_audio.path,
                            'bitrate': stream_audio.parameters.bitrate,
                        },
                    }
                    if stream_video is not None:
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
