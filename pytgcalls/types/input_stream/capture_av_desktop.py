from typing import Dict
from typing import Optional

from ntgcalls import InputMode

from ...ffmpeg import build_command
from ...ffmpeg import check_stream
from ...media_devices.screen_info import ScreenInfo
from .audio_parameters import AudioParameters
from .audio_stream import AudioStream
from .smart_stream import SmartStream
from .video_parameters import VideoParameters
from .video_stream import VideoStream


class CaptureAVDesktop(SmartStream):
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
        self._audio_data = (
            additional_ffmpeg_parameters,
            self._audio_path,
            audio_parameters,
            [],
            headers,
        )
        super().__init__(
            AudioStream(
                InputMode.Shell,
                ' '.join(
                    build_command(
                        'ffmpeg',
                        *self._audio_data,
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

    async def check_stream(self):
        await check_stream(
            *self._audio_data,
        )
