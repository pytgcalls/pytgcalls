from deprecation import deprecated

from ...media_devices.screen_info import ScreenInfo
from .media_stream import MediaStream
from .video_parameters import VideoParameters


@deprecated(
    deprecated_in='1.1.0',
    details='This class is no longer supported.'
            'Use pytgcalls.types.input_stream.MediaStream instead.',
)
class CaptureVideoDesktop(MediaStream):
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
