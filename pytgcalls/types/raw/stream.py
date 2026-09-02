from ...statictypes import statictypes
from ..py_object import PyObject
from .audio_stream import AudioStream
from .video_stream import VideoStream


class Stream(PyObject):
    @statictypes
    def __init__(
        self,
        microphone: AudioStream | None = None,
        speaker: AudioStream | None = None,
        camera: VideoStream | None = None,
        screen: VideoStream | None = None,
    ):
        self.microphone: AudioStream | None = microphone
        self.speaker: AudioStream | None = speaker
        self.camera: VideoStream | None = camera
        self.screen: VideoStream | None = screen
