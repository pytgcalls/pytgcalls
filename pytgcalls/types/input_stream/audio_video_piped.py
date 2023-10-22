from typing import Dict
from typing import Optional

from ntgcalls import InputMode

from ...ffmpeg import build_command
from ...ffmpeg import check_stream
from .audio_parameters import AudioParameters
from .audio_stream import AudioStream
from .smart_stream import SmartStream
from .video_parameters import VideoParameters
from .video_stream import VideoStream


class AudioVideoPiped(SmartStream):
    def __init__(
        self,
        path: str,
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
    ):
        self._path = path
        self._audio_data = (
            additional_ffmpeg_parameters,
            self._path,
            audio_parameters,
            [],
            headers,
        )
        self._video_data = (
            additional_ffmpeg_parameters,
            self._path,
            video_parameters,
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
                        *self._video_data,
                    ),
                ),
                video_parameters,
            ),
        )

    async def check_stream(self):
        await check_stream(
            *self._audio_data,
        )
        await check_stream(
            *self._video_data,
        )
        self.stream_video.path = ' '.join(
            build_command(
                'ffmpeg',
                *self._video_data,
            ),
        )
