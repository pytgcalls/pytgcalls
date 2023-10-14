from ntgcalls import InputMode

from ...ffmpeg import build_command
from ...media_devices.device_info import DeviceInfo
from ...media_devices.screen_info import ScreenInfo
from .audio_parameters import AudioParameters
from .audio_stream import AudioStream
from .smart_stream import SmartStream
from .video_parameters import VideoParameters
from .video_stream import VideoStream


class CaptureAVDeviceDesktop(SmartStream):
    def __init__(
        self,
        audio_info: DeviceInfo,
        screen_info: ScreenInfo,
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
    ):
        self._audio_path = audio_info.build_ffmpeg_command()
        self._video_path = screen_info.build_ffmpeg_command(
            video_parameters.frame_rate,
        )
        audio_data = (
            '',
            self._audio_path,
            audio_parameters,
            audio_info.ffmpeg_parameters,
        )
        super().__init__(
            AudioStream(
                InputMode.Shell,
                ' '.join(
                    build_command(
                        'ffmpeg',
                        *audio_data,
                    ),
                ),
                audio_parameters,
            ),
            VideoStream(
                InputMode.Shell,
                ' '.join(
                    build_command(
                        'ffmpeg',
                        '',
                        self._video_path,
                        video_parameters,
                        screen_info.ffmpeg_parameters,
                    ),
                ),
                video_parameters,
            ),
        )
