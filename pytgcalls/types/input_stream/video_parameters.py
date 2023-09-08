from ..py_object import PyObject


class VideoParameters(PyObject):

    def __init__(
        self,
        width: int = 640,
        height: int = 360,
        frame_rate: int = 20,
    ):
        self.width: int = width
        self.height: int = height
        self.frame_rate: int = frame_rate
