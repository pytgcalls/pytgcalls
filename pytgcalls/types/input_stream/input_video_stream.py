import deprecation
from ntgcalls import InputMode

from ... import __version__
from .video_parameters import VideoParameters
from .video_stream import VideoStream


@deprecation.deprecated(
    deprecated_in='1.0.0.dev1',
    current_version=__version__,
    details='Use pytgcalls.VideoStream instead.',
)
class InputVideoStream(VideoStream):
    def __init__(
        self,
        path: str,
        parameters: VideoParameters = VideoParameters(),
        header_enabled: bool = False,
    ):
        super().__init__(InputMode.File, path, parameters, header_enabled)
