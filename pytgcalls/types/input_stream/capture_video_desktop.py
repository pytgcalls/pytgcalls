from ntgcalls import InputMode

from ...ffmpeg import build_ffmpeg_command
from ...media_devices.screen_info import ScreenInfo
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
        super().__init__(
            stream_video=VideoStream(
                InputMode.Shell,
                build_ffmpeg_command(
                    '',
                    self._path,
                    video_parameters,
                    screen_info.ffmpeg_parameters,
                ),
            ),
        )
