from ..py_object import PyObject


class VideoParameters(PyObject):
    """Video parameters of the stream

    Attributes:
        width (``int``):
            Video width
        height (``int``):
            Video height
        frame_rate (``int``):
            Framerate of video

    Parameters:
        width (``int``):
            Video width
        height (``int``):
            Video height
        frame_rate (``int``):
            Framerate of video
    """

    def __init__(
        self,
        width: int = 640,
        height: int = 360,
        frame_rate: int = 20,
    ):
        self.width: int = width
        self.height: int = height
        self.frame_rate: int = frame_rate
