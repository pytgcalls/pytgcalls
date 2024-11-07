from ntgcalls import MediaSource

from ...statictypes import statictypes
from ..py_object import PyObject
from .audio_parameters import AudioParameters


class AudioStream(PyObject):
    @statictypes
    def __init__(
        self,
        media_source: MediaSource,
        path: str,
        parameters: AudioParameters = AudioParameters(),
    ):
        self.media_source: MediaSource = media_source
        self.path: str = path
        self.parameters: AudioParameters = parameters
