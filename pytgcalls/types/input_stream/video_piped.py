from typing import Dict
from typing import Optional

from ...ffprobe import FFprobe
from .input_stream import Stream
from .input_video_stream import InputVideoStream
from .video_parameters import VideoParameters


# TODO refactor needed
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
            stream_video=InputVideoStream(
                f'fifo://{path}',
                video_parameters,
            ),
        )

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)
