from deprecation import deprecated

from ....media_devices import ScreenInfo
from ....statictypes import statictypes
from ...raw import VideoParameters
from ..media_stream import MediaStream


@deprecated(
    deprecated_in='1.1.0',
    details='Use pytgcalls.types.MediaStream instead.',
)
class CaptureVideoDesktop(MediaStream):
    @statictypes
    def __init__(
        self,
        screen_info: ScreenInfo,
        video_parameters: VideoParameters = VideoParameters(),
    ):
        super().__init__(
            media_path=screen_info,
            video_parameters=video_parameters,
            audio_flags=MediaStream.IGNORE,
            video_flags=MediaStream.REQUIRED,
        )
