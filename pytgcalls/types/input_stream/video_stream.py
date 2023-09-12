from ntgcalls import InputMode

from .video_parameters import VideoParameters


class VideoStream:
    def __init__(
        self,
        input_mode: InputMode,
        path: str,
        parameters: VideoParameters = VideoParameters(),
    ):
        self.input_mode: InputMode = input_mode
        self.path: str = path
        self.parameters: VideoParameters = parameters
