from ntgcalls import InputMode

from ...ffprobe import FFprobe
from ...media_devices.screen_info import ScreenInfo
from .input_stream import InputStream
from .video_parameters import VideoParameters
from .video_stream import VideoStream


class CaptureVideoDesktop(InputStream):
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
                InputMode.FFmpeg,
                f'screen://{self._path}',
                video_parameters,
            ),
        )

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)
