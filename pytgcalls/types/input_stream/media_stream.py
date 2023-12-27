from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
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
from .stream import Stream
from .video_parameters import VideoParameters
from .video_stream import VideoStream


class MediaStream(Stream):
    AUTO_DETECT = 1
    IGNORE = 4
    REQUIRED = 8

    def __init__(
        self,
        media_path: Union[str, ScreenInfo, DeviceInfo],
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
        audio_path: Optional[Union[str, DeviceInfo]] = None,
        audio_flags: int = AUTO_DETECT,
        video_flags: int = AUTO_DETECT,
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

        self._audio_flags = audio_flags
        self._video_flags = video_flags
        self._audio_data: Tuple[
            str,
            Union[str, ScreenInfo, DeviceInfo],
            AudioParameters,
            List[str],
            Optional[Dict[str, str]],
        ] = (
            additional_ffmpeg_parameters,
            audio_path if audio_path else media_path,
            audio_parameters,
            [],
            headers,
        )
        self._video_data: Tuple[
            str,
            Union[str, ScreenInfo, DeviceInfo],
            VideoParameters,
            List[str],
            Optional[Dict[str, str]],
        ] = (
            additional_ffmpeg_parameters,
            media_path,
            video_parameters,
            [],
            headers,
        )
        super().__init__(
            stream_audio=None if audio_flags == self.IGNORE else
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
            stream_video=None if video_flags == self.IGNORE else
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
        if not self._audio_flags == self.IGNORE:
            try:
                await check_stream(
                    *self._audio_data,
                )
            except NoAudioSourceFound as e:
                if self._audio_flags == self.REQUIRED:
                    raise e
                self.stream_audio = None

        if not self._video_flags == self.IGNORE:
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
                if self._video_flags == self.REQUIRED:
                    raise e
                self.stream_video = None
