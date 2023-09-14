from ntgcalls import InputMode

from ...ffprobe import FFprobe
from ...media_devices.device_info import DeviceInfo
from ...media_devices.screen_info import ScreenInfo
from ...ffmpeg import build_ffmpeg_command
from .audio_parameters import AudioParameters
from .audio_stream import AudioStream
from .input_stream import Stream
from .video_parameters import VideoParameters
from .video_stream import VideoStream


class CaptureAVDeviceDesktop(Stream):
    def __init__(
        self,
        audio_info: DeviceInfo,
        screen_info: ScreenInfo,
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
    ):
        self._audio_path = audio_info.build_ffmpeg_command()
        self.audio_ffmpeg: str = audio_info.ffmpeg_parameters
        self._video_path = screen_info.build_ffmpeg_command(
            video_parameters.frame_rate,
        )
        self.video_ffmpeg: str = screen_info.ffmpeg_parameters
        self.raw_headers = None
        super().__init__(
            AudioStream(
                InputMode.Shell,
                build_ffmpeg_command(
                    self.audio_ffmpeg,
                    self._audio_path,
                    'audio',
                    audio_parameters,
                ),
            ),
            VideoStream(
                InputMode.Shell,
                build_ffmpeg_command(
                    self.video_ffmpeg,
                    self._video_path,
                    'video',
                    video_parameters,
                ),
            ),
        )

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)
