from pathlib import Path
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
    IGNORE = 2
    REQUIRED = 4

    def __init__(
        self,
        media_path: Union[str, Path, ScreenInfo, DeviceInfo],
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
        audio_path: Optional[Union[str, Path, DeviceInfo]] = None,
        audio_flags: Optional[int] = AUTO_DETECT,
        video_flags: Optional[int] = AUTO_DETECT,
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: Optional[str] = None,
    ):
        if isinstance(media_path, DeviceInfo):
            media_path = media_path.build_ffmpeg_command()
        elif isinstance(media_path, ScreenInfo):
            media_path = media_path.build_ffmpeg_command(
                video_parameters.frame_rate,
            )
        elif isinstance(media_path, Path):
            media_path = str(media_path)

        if isinstance(audio_path, DeviceInfo):
            audio_path = audio_path.build_ffmpeg_command()
        elif isinstance(audio_path, Path):
            audio_path = str(audio_path)

        self._audio_flags = audio_flags
        self._video_flags = video_flags
        self._audio_data: Tuple[
            Optional[str],
            Union[str, Path, ScreenInfo, DeviceInfo],
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
            Optional[str],
            Union[str, Path, ScreenInfo, DeviceInfo],
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
