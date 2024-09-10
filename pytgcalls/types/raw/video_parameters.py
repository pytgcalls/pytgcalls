from ...statictypes import statictypes
from ..py_object import PyObject
from ..stream.video_quality import VideoQuality


class VideoParameters(PyObject):
    @statictypes
    def __init__(
        self,
        width: int = 640,
        height: int = 360,
        frame_rate: int = 20,
        adjust_by_height: bool = True,
    ):
        max_w, max_h, max_fps = max(
            VideoQuality, key=lambda x: x.value[0],
        ).value
        self.width: int = min(width, max_w)
        self.height: int = min(height, max_h)
        self.frame_rate: int = min(frame_rate, max_fps)
        self.adjust_by_height: bool = adjust_by_height
