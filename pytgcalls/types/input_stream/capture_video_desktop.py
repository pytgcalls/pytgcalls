from ntgcalls import InputMode

from ...ffprobe import FFprobe
from ...media_devices.screen_info import ScreenInfo
from ...methods.utilities import ffmpeg_tools
from .input_stream import Stream
from .video_parameters import VideoParameters
from .video_stream import VideoStream


class CaptureVideoDesktop(Stream):
    def __init__(
        self,
        screen_info: ScreenInfo,
        video_parameters: VideoParameters = VideoParameters(),
    ):
        self._path = screen_info.build_ffmpeg_command(
            video_parameters.frame_rate,
        )
        self.ffmpeg_parameters: str = screen_info.ffmpeg_parameters
        self.raw_headers = None
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
