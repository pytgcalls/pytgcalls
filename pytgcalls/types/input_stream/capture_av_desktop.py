from typing import Dict
from typing import Optional

from ntgcalls import InputMode

from ...ffmpeg import build_ffmpeg_command
from ...media_devices.screen_info import ScreenInfo
from .audio_parameters import AudioParameters
from .audio_stream import AudioStream
from .input_stream import Stream
from .video_parameters import VideoParameters
from .video_stream import VideoStream


class CaptureAVDesktop(Stream):
    def __init__(
        self,
        audio_path: str,
        screen_info: ScreenInfo,
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
    ):
        self._audio_path = audio_path
        self._video_path = screen_info.build_ffmpeg_command(
            video_parameters.frame_rate,
        )
        super().__init__(
            AudioStream(
                InputMode.Shell,
                build_ffmpeg_command(
                    additional_ffmpeg_parameters,
                    self._audio_path,
                    audio_parameters,
                    [],
                    headers,
                ),
                audio_parameters,
            ),
            VideoStream(
                InputMode.Shell,
                build_ffmpeg_command(
                    '',
                    self._video_path,
                    video_parameters,
                    screen_info.ffmpeg_parameters,
                ),
                video_parameters,
            ),
        )
