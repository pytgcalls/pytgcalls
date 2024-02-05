from typing import Dict
from typing import Optional

from deprecation import deprecated

from ....media_devices import ScreenInfo
from ....statictypes import statictypes
from ...raw import AudioParameters
from ...raw import VideoParameters
from ..media_stream import MediaStream


@deprecated(
    deprecated_in='1.1.0',
    details='Use pytgcalls.types.MediaStream instead.',
)
class CaptureAVDesktop(MediaStream):
    @statictypes
    def __init__(
        self,
        audio_path: str,
        screen_info: ScreenInfo,
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
    ):
        super().__init__(
            media_path=screen_info,
            audio_parameters=audio_parameters,
            video_parameters=video_parameters,
            audio_path=audio_path,
            audio_flags=MediaStream.REQUIRED,
            video_flags=MediaStream.REQUIRED,
            headers=headers,
            ffmpeg_parameters=additional_ffmpeg_parameters,
        )
