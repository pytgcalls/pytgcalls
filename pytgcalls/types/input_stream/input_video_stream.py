from .video_parameters import VideoParameters
from ..py_object import PyObject


class InputVideoStream(PyObject):
    def __init__(
        self,
        path: str,
        parameters: VideoParameters = VideoParameters(),
    ):
        self.path: str = path
        self.parameters: VideoParameters = parameters
