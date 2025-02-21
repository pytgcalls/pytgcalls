import logging
from enum import auto
from pathlib import Path
from typing import Dict
from typing import Optional
from typing import Union

from ntgcalls import MediaSource

from ...exceptions import ImageSourceFound
from ...exceptions import LiveStreamFound
from ...exceptions import NoAudioSourceFound
from ...exceptions import NoVideoSourceFound
from ...ffmpeg import build_command
from ...ffmpeg import check_stream
from ...media_devices.input_device import InputDevice
from ...media_devices.screen_device import ScreenDevice
from ...statictypes import statictypes
from ...ytdlp import YtDlp
from ..flag import Flag
from ..raw.audio_parameters import AudioParameters
from ..raw.audio_stream import AudioStream
from ..raw.stream import Stream
from ..raw.video_parameters import VideoParameters
from ..raw.video_stream import VideoStream
from ..stream.audio_quality import AudioQuality
from ..stream.video_quality import VideoQuality
from .external_media import ExternalMedia

py_logger = logging.getLogger('pytgcalls')


class MediaStream(Stream):
    class Flags(Flag):
        AUTO_DETECT = auto()
        REQUIRED = auto()
        IGNORE = auto()

    @statictypes
    def __init__(
        self,
        media_path: Union[str, Path, InputDevice, ExternalMedia],
        audio_parameters: Union[
            AudioParameters,
            AudioQuality,
        ] = AudioQuality.HIGH,
        video_parameters: Union[
            VideoParameters,
            VideoQuality,
        ] = VideoQuality.SD_480p,
        audio_path: Optional[
            Union[
                str, Path,
                InputDevice, ExternalMedia,
            ]
        ] = None,
        audio_flags: Optional[Flags] = Flags.AUTO_DETECT,
        video_flags: Optional[Flags] = Flags.AUTO_DETECT,
        headers: Optional[Dict[str, str]] = None,
        ffmpeg_parameters: Optional[str] = None,
        ytdlp_parameters: Optional[str] = None,
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
            self._video_parameters = VideoParameters(
                *video_parameters.value,
                adjust_by_height=False,
            )

        self._media_path: Optional[str] = None
        self._audio_path: Optional[str] = None
        self._is_media_device: bool = False
        self._is_audio_device: bool = False
        self._is_audio_external: bool = False
        self._is_video_external: bool = False
        if isinstance(media_path, str):
            self._media_path = media_path
        elif isinstance(media_path, Path):
            self._media_path = str(media_path)
        elif isinstance(media_path, ExternalMedia):
            if media_path & ExternalMedia.AUDIO:
                self._is_audio_external = True
            if media_path & ExternalMedia.VIDEO:
                self._is_video_external = True
        elif isinstance(media_path, (InputDevice, ScreenDevice)):
            print('MediaStream', media_path.is_video)
            if media_path.is_video:
                self._media_path = media_path.metadata
                self._is_media_device = True
            else:
                self._audio_path = media_path.metadata
                self._is_audio_device = True

        if isinstance(audio_path, str):
            self._audio_path = audio_path
        elif isinstance(audio_path, Path):
            self._audio_path = str(audio_path)
        elif isinstance(audio_path, ExternalMedia):
            self._audio_path = ''
            if audio_path == ExternalMedia.AUDIO:
                if self._is_audio_external:
                    py_logger.warning(
                        'Audio path is already an audio source, '
                        'ignoring audio path',
                    )
                self._is_audio_external = True
            else:
                raise ValueError('Audio path must be an audio source')
        elif isinstance(audio_path, (InputDevice, ScreenDevice)):
            if audio_path.is_video:
                raise ValueError('Audio path must be an audio device')
            self._audio_path = audio_path.metadata
            self._is_audio_device = True

        self._audio_flags = self._filter_flags(audio_flags)
        self._video_flags = self._filter_flags(video_flags)
        self._ffmpeg_parameters = ffmpeg_parameters
        self._ytdlp_parameters = ytdlp_parameters
        self._headers = headers
        super().__init__(
            microphone=None
            if (
                self._audio_flags & MediaStream.Flags.IGNORE or
                self._media_path is None and
                self._audio_path is None
            ) and not self._is_audio_external else
            AudioStream(
                MediaSource.DEVICE,
                self._audio_path,
                self._audio_parameters,
            )
            if self._is_audio_device else
            AudioStream(
                MediaSource.EXTERNAL,
                '',
                self._audio_parameters,
            )
            if self._is_audio_external else
            AudioStream(
                MediaSource.SHELL,
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
            camera=None
            if (
                self._video_flags & MediaStream.Flags.IGNORE or
                self._media_path is None
            ) and not self._is_video_external else
            VideoStream(
                MediaSource.DESKTOP if isinstance(media_path, ScreenDevice)
                else MediaSource.DEVICE,
                self._media_path,
                self._video_parameters,
            )
            if self._is_media_device else
            VideoStream(
                MediaSource.EXTERNAL,
                '',
                self._video_parameters,
            )
            if self._is_video_external else
            VideoStream(
                MediaSource.SHELL,
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
        if not self._video_flags & MediaStream.Flags.IGNORE and \
                not self._is_video_external:
            if self._is_media_device:
                if not self._media_path:
                    self.camera = None
            elif self._media_path:
                if YtDlp.is_valid(self._media_path):
                    links = await YtDlp.extract(
                        self._media_path,
                        self._video_parameters,
                        self._ytdlp_parameters,
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
                    self.camera.path = ' '.join(
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
                    if self._video_flags & MediaStream.Flags.REQUIRED:
                        raise e
                    self.camera = None
            else:
                self.camera = None

        if not self._is_media_device:
            self._audio_path = self._audio_path \
                if self._audio_path else self._media_path

        if not self._audio_flags & MediaStream.Flags.IGNORE and \
                not self._is_audio_external:
            if self._is_audio_device:
                if not self._audio_path:
                    self.microphone = None
            elif self._audio_path:
                if YtDlp.is_valid(self._audio_path):
                    self._audio_path = (
                        await YtDlp.extract(
                            self._audio_path,
                            self._video_parameters,
                            self._ytdlp_parameters,
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
                    self.microphone.path = ' '.join(
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
                    if self._audio_flags & MediaStream.Flags.REQUIRED:
                        raise e
                    self.microphone = None
            else:
                self.microphone = None

    @staticmethod
    def _filter_flags(flags: Optional[Flags]) -> Flags:
        combined_flags = [
            MediaStream.Flags.AUTO_DETECT,
            MediaStream.Flags.IGNORE, MediaStream.Flags.REQUIRED,
        ]
        combined_flags_value = MediaStream.Flags(
            sum([flag.value for flag in combined_flags]),
        )
        if not flags:
            flags = min(combined_flags, key=lambda flag: flag.value)
        if flags & ~combined_flags_value != 0:
            flags |= min(combined_flags, key=lambda flag: flag.value)
        potential_flag = max(
            [flag for flag in combined_flags if flags & flag],
            key=lambda flag: flag.value,
        )
        return flags & ~combined_flags_value | potential_flag
