from deprecation import deprecated
from ntgcalls import InputMode

from .video_parameters import VideoParameters
from .video_stream import VideoStream


@deprecated(
    deprecated_in='1.0.0.dev1',
    details='Use pytgcalls.VideoStream instead.',
)
class InputVideoStream(VideoStream):
    def __init__(
        self,
        path: str,
        parameters: VideoParameters = VideoParameters(),
        header_enabled: bool = False,
    ):
        super().__init__(InputMode.File, path, parameters)
        self.header_enabled = header_enabled
