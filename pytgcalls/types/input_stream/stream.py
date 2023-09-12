from typing import Optional

from ..py_object import PyObject
from .audio_stream import AudioStream
from .video_stream import VideoStream


class Stream(PyObject):
    def __init__(
        self,
        stream_audio: Optional[AudioStream] = None,
        stream_video: Optional[VideoStream] = None,
    ):
        self.stream_audio: Optional[AudioStream] = stream_audio
        self.stream_video: Optional[VideoStream] = stream_video
