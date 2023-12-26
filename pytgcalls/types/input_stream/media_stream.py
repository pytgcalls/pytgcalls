from typing import Dict
from typing import Optional
from typing import Union

from ntgcalls import InputMode

from ...exceptions import ImageSourceFound
from ...exceptions import NoAudioSourceFound
from ...exceptions import NoVideoSourceFound
from ...ffmpeg import build_command
from ...ffmpeg import check_stream
from ...media_devices import DeviceInfo
from ...media_devices import ScreenInfo
from .audio_parameters import AudioParameters
from .audio_stream import AudioStream
from .smart_stream import SmartStream
from .video_parameters import VideoParameters
from .video_stream import VideoStream


class MediaStream(SmartStream):
    def __init__(
        self,
        media_path: Union[str, ScreenInfo, DeviceInfo],
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
        audio_path: Union[str, DeviceInfo] = None,
        requires_audio=False,
        requires_video=False,
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
    ):
        if isinstance(media_path, DeviceInfo):
            media_path = media_path.build_ffmpeg_command()

        if isinstance(media_path, ScreenInfo):
            media_path = media_path.build_ffmpeg_command(
                video_parameters.frame_rate,
            )

        if isinstance(audio_path, DeviceInfo):
            audio_path = audio_path.build_ffmpeg_command()

        self._audio_data = (
            additional_ffmpeg_parameters,
            audio_path if audio_path else media_path,
            audio_parameters,
            [],
            headers,
        )
        self._video_data = (
            additional_ffmpeg_parameters,
            media_path,
            video_parameters,
            [],
            headers,
        )
        self._requires_audio = requires_audio
        self._requires_video = requires_video
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
        try:
            await check_stream(
                *self._audio_data,
            )
        except NoAudioSourceFound as e:
            if self._requires_audio:
                raise e
            self.stream_audio = None

        try:
            try:
                await check_stream(
                    *self._video_data,
                )
            except ImageSourceFound:
                self._video_data = (
                    self._video_data[0],
                    self._video_data[1],
                    self._video_data[2],
                    [
                        '-loop',
                        '1',
                        '-framerate',
                        '1',
                    ],
                    self._video_data[4],
                )
            self.stream_video.path = ' '.join(
                build_command(
                    'ffmpeg',
                    *self._video_data,
                ),
            )
        except NoVideoSourceFound as e:
            if self._requires_video:
                raise e
            self.stream_video = None
