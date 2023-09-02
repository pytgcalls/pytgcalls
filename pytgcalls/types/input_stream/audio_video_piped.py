from typing import Dict
from typing import Optional

from ntgcalls import InputMode

from ...ffprobe import FFprobe
from .audio_parameters import AudioParameters
from .audio_stream import AudioStream
from .input_stream import InputStream
from .video_parameters import VideoParameters
from .video_stream import VideoStream
from .video_tools import check_video_params


class AudioVideoPiped(InputStream):
    def __init__(
        self,
        path: str,
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
    ):
        self._path = path
        self.ffmpeg_parameters = additional_ffmpeg_parameters
        self.raw_headers = headers
        super().__init__(
            AudioStream(
                InputMode.FFmpeg,
                f'fifo://{path}',
                audio_parameters,
            ),
            VideoStream(
                InputMode.FFmpeg,
                f'fifo://{path}',
                video_parameters,
            ),
        )
        self.lip_sync = True

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)

    async def check_pipe(self):
        dest_width, dest_height, header = await FFprobe.check_file(
            self._path,
            needed_audio=True,
            needed_video=True,
            needed_image=False,
            headers=self.raw_headers,
        )
        width, height = check_video_params(
            self.stream_video.parameters,
            dest_width,
            dest_height,
        )
        self.stream_video.header_enabled = header
        self.stream_audio.header_enabled = header
        self.stream_video.parameters.width = width
        self.stream_video.parameters.height = height
