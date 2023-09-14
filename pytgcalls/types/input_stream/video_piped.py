from typing import Dict
from typing import Optional

from ntgcalls import InputMode

from ...ffmpeg import build_ffmpeg_command
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
        super().__init__(
            stream_video=VideoStream(
                InputMode.Shell,
                build_ffmpeg_command(
                    additional_ffmpeg_parameters,
                    self._path,
                    video_parameters,
                    [],
                    headers,
                ),
            ),
        )
