from ntgcalls import InputMode

from ...statictypes import statictypes
from .video_parameters import VideoParameters


class VideoStream:
    @statictypes
    def __init__(
        self,
        input_mode: InputMode,
        path: str,
        parameters: VideoParameters = VideoParameters(),
    ):
        self.input_mode: InputMode = input_mode
        self.path: str = path
        self.parameters: VideoParameters = parameters
