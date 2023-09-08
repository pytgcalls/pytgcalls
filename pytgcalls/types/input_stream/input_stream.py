from typing import Optional

from ..py_object import PyObject
from .input_audio_stream import AudioStream
from .video_stream import VideoStream


class InputStream(PyObject):

    def __init__(
        self,
        stream_audio: Optional[AudioStream] = None,
        stream_video: Optional[VideoStream] = None,
        lip_sync: bool = False,
    ):
        self.stream_audio: Optional[AudioStream] = stream_audio
        self.stream_video: Optional[VideoStream] = stream_video
        self.lip_sync = lip_sync
