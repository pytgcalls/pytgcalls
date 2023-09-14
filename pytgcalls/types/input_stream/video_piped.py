from typing import Dict
from typing import Optional

from ntgcalls import InputMode

from ...ffprobe import FFprobe
from ...methods.utilities import ffmpeg_tools
from .input_stream import Stream
from .video_parameters import VideoParameters
from .video_stream import VideoStream


class VideoPiped(Stream):
    def __init__(
            self,
            path: str,
            video_parameters: VideoParameters = VideoParameters(),
            headers: Optional[Dict[str, str]] = None,
            additional_ffmpeg_parameters: str = '',
    ):
        self._path = path
        self.ffmpeg_parameters = additional_ffmpeg_parameters
        self.raw_headers = headers
        super().__init__(
            stream_video=VideoStream(
                InputMode.Shell,
                ffmpeg_tools.build_ffmpeg_command(
                    self.ffmpeg_parameters,
                    self._path,
                    'video',
                    video_parameters,
                ),
            ),
        )

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)
