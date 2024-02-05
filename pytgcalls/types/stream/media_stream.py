from pathlib import Path
from typing import Dict
from typing import Optional
from typing import Union

from ntgcalls import InputMode

from ...exceptions import ImageSourceFound
from ...exceptions import LiveStreamFound
from ...exceptions import NoAudioSourceFound
from ...exceptions import NoVideoSourceFound
from ...ffmpeg import build_command
from ...ffmpeg import check_stream
from ...media_devices import DeviceInfo
from ...media_devices import ScreenInfo
from ...statictypes import statictypes
from ...ytdlp import YtDlp
from ..raw.audio_parameters import AudioParameters
from ..raw.audio_stream import AudioStream
from ..raw.stream import Stream
from ..raw.video_parameters import VideoParameters
from ..raw.video_stream import VideoStream
from ..stream.audio_quality import AudioQuality
from ..stream.video_quality import VideoQuality


class MediaStream(Stream):
    AUTO_DETECT = 1
    IGNORE = 2
    REQUIRED = 4

    @statictypes
    def __init__(
        self,
        media_path: Union[str, Path, ScreenInfo, DeviceInfo],
        audio_parameters: Union[
            AudioParameters,
            AudioQuality,
        ] = AudioQuality.HIGH,
        video_parameters: Union[
            VideoParameters,
            VideoQuality,
        ] = VideoQuality.SD_480p,
        audio_path: Optional[Union[str, Path, DeviceInfo]] = None,
        audio_flags: Optional[int] = AUTO_DETECT,
        video_flags: Optional[int] = AUTO_DETECT,
        headers: Optional[Dict[str, str]] = None,
        ffmpeg_parameters: Optional[str] = None,
    ):
        self._audio_parameters: AudioParameters
        self._video_parameters: VideoParameters
        if isinstance(audio_parameters, AudioParameters):
            self._audio_parameters = audio_parameters
        elif isinstance(audio_parameters, AudioQuality):
            self._audio_parameters = AudioParameters(*audio_parameters.value)

        if isinstance(video_parameters, VideoParameters):
            self._video_parameters = video_parameters
        elif isinstance(video_parameters, VideoQuality):
            self._video_parameters = VideoParameters(*video_parameters.value)

        self._media_path: Optional[str] = None
        self._audio_path: Optional[str] = None
        if isinstance(media_path, str):
            self._media_path = media_path
        elif isinstance(media_path, Path):
            self._media_path = str(media_path)
        elif isinstance(media_path, DeviceInfo):
            self._media_path = media_path.build_ffmpeg_command()
        elif isinstance(media_path, ScreenInfo):
            self._media_path = media_path.build_ffmpeg_command(
                self._video_parameters.frame_rate,
            )

        if isinstance(audio_path, str):
            self._audio_path = audio_path
        elif isinstance(audio_path, Path):
            self._audio_path = str(audio_path)
        elif isinstance(audio_path, DeviceInfo):
            self._audio_path = audio_path.build_ffmpeg_command()

        self._audio_flags = audio_flags
        self._video_flags = video_flags
        self._ffmpeg_parameters = ffmpeg_parameters
        self._headers = headers
        super().__init__(
            stream_audio=None if audio_flags == self.IGNORE else
            AudioStream(
                InputMode.Shell,
                ' '.join(
                    build_command(
                        'ffmpeg',
                        self._ffmpeg_parameters,
                        self._audio_path,
                        self._audio_parameters,
                        [],
                        self._headers,
                        False,
                    ),
                ),
                self._audio_parameters,
            ),
            stream_video=None if video_flags == self.IGNORE else
            VideoStream(
                InputMode.Shell,
                ' '.join(
                    build_command(
                        'ffmpeg',
                        self._ffmpeg_parameters,
                        self._media_path,
                        self._video_parameters,
                        [],
                        self._headers,
                        False,
                    ),
                ),
                self._video_parameters,
            ),
        )

    async def check_stream(self):
        if not self._video_flags == self.IGNORE:
            if YtDlp.is_valid(self._media_path):
                links = await YtDlp.extract(
                    self._media_path,
                    self._video_parameters,
                )
                self._media_path = links[0]
                if not self._audio_path:
                    self._audio_path = links[1]
            try:
                image_commands = []
                live_stream = False
                try:
                    await check_stream(
                        self._ffmpeg_parameters,
                        self._media_path,
                        self._video_parameters,
                        [],
                        self._headers,
                    )
                except ImageSourceFound:
                    image_commands = [
                        '-loop',
                        '1',
                        '-framerate',
                        '1',
                    ]
                except LiveStreamFound:
                    live_stream = True
                self.stream_video.path = ' '.join(
                    build_command(
                        'ffmpeg',
                        self._ffmpeg_parameters,
                        self._media_path,
                        self._video_parameters,
                        image_commands,
                        self._headers,
                        live_stream,
                    ),
                )
            except NoVideoSourceFound as e:
                if self._video_flags == self.REQUIRED:
                    raise e
                self.stream_video = None

        self._audio_path = self._audio_path \
            if self._audio_path else self._media_path

        if not self._audio_flags == self.IGNORE:
            if YtDlp.is_valid(self._audio_path):
                self._audio_path = (
                    await YtDlp.extract(
                        self._audio_path,
                        self._video_parameters,
                    )
                )[1]

            try:
                live_stream = False
                try:
                    await check_stream(
                        self._ffmpeg_parameters,
                        self._audio_path,
                        self._audio_parameters,
                        [],
                        self._headers,
                    )
                except LiveStreamFound:
                    live_stream = True
                self.stream_audio.path = ' '.join(
                    build_command(
                        'ffmpeg',
                        self._ffmpeg_parameters,
                        self._audio_path,
                        self._audio_parameters,
                        [],
                        self._headers,
                        live_stream,
                    ),
                )
            except NoAudioSourceFound as e:
                if self._audio_flags == self.REQUIRED:
                    raise e
                self.stream_audio = None
