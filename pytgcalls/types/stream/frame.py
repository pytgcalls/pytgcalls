from ntgcalls import Codec
from ntgcalls import VideoRotation

from ...types.update import PyObject


class Frame(PyObject):
    class Info(PyObject):
        def __init__(
            self,
            capture_time: int = 0,
            width: int = 0,
            height: int = 0,
            rotation: VideoRotation = VideoRotation.VIDEO_ROTATION_0,
            codec: Codec | None = None,
        ):
            self.capture_time = capture_time
            self.width = width
            self.height = height
            self.rotation = rotation
            self.codec = codec

    def __init__(
        self,
        ssrc: int,
        frame: bytes,
        info: Info,
    ):
        self.ssrc = ssrc
        self.frame = frame
        self.info = info
