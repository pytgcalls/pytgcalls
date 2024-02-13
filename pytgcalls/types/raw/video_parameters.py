from deprecation import deprecated
from ...statictypes import statictypes
from ..py_object import PyObject
from ..stream.video_quality import VideoQuality

class VideoParameters(PyObject):
    @statictypes
    def __init__(self, width: int = 640, height: int = 360, frame_rate: int = 20, bitrate: int = 1000):
        max_w, max_h, max_fps, max_bitrate = max(VideoQuality, key=lambda x: x.value[0]).value
        self.width: int = min(width, max_w)
        self.height: int = min(height, max_h)
        self.frame_rate: int = min(frame_rate, max_fps)
        self.bitrate: int = min(bitrate, max_bitrate)

    @staticmethod
    @deprecated(deprecated_in='2.0.0', details='Use VideoQuality.XXX directly without VideoParameters instead.')
    @statictypes
    def from_quality(quality: VideoQuality):
        return VideoParameters(*quality.value)

    def to_quality(self) -> VideoQuality:
        closest_quality = min(VideoQuality, key=lambda x: ((x.value[0] - self.width) ** 2 +
                                                           (x.value[1] - self.height) ** 2 +
                                                           (x.value[2] - self.frame_rate) ** 2 +
                                                           (x.value[3] - self.bitrate) ** 2))
        return closest_quality

    def calculate_video_size(self, duration_seconds: float) -> int:
        return (self.bitrate * duration_seconds) // 8
