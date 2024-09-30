from typing import Optional

from ...statictypes import statictypes
from ..py_object import PyObject
from .audio_stream import AudioStream
from .video_stream import VideoStream


class Stream(PyObject):
    @statictypes
    def __init__(
        self,
        microphone: Optional[AudioStream] = None,
        speaker: Optional[AudioStream] = None,
        camera: Optional[VideoStream] = None,
        screen: Optional[VideoStream] = None,
    ):
        self.microphone: Optional[AudioStream] = microphone
        self.speaker: Optional[AudioStream] = speaker
        self.camera: Optional[VideoStream] = camera
        self.screen: Optional[VideoStream] = screen
