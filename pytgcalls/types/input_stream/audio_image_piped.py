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


class AudioImagePiped(SmartStream):
    def __init__(
        self,
        audio_path: str,
        image_path: str,
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
    ):
        self._image_path = image_path
        self._audio_path = audio_path
        video_parameters.frame_rate = 1
        self._audio_data = (
            additional_ffmpeg_parameters,
            self._audio_path,
            audio_parameters,
            [],
            headers,
        )
        self._video_data = (
            additional_ffmpeg_parameters,
            self._image_path,
            video_parameters,
            [
                '-loop',
                '1',
                '-framerate',
                str(video_parameters.frame_rate),
            ],
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
            need_image=True,
        )
        self.stream_video.path = ' '.join(
            build_command(
                'ffmpeg',
                *self._video_data,
            ),
        )
