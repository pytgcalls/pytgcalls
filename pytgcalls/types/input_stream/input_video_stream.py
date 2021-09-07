from .video_parameters import VideoParameters


class InputVideoStream:
    def __init__(
        self,
        path: str,
        parameters: VideoParameters = VideoParameters(),
    ):
        self.path: str = path
        self.parameters: VideoParameters = parameters
