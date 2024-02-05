from ntgcalls import InputMode

from ...statictypes import statictypes
from ..py_object import PyObject
from .audio_parameters import AudioParameters


class AudioStream(PyObject):
    @statictypes
    def __init__(
        self,
        input_mode: InputMode,
        path: str,
        parameters: AudioParameters = AudioParameters(),
    ):
        self.input_mode: InputMode = input_mode
        self.path: str = path
        self.parameters: AudioParameters = parameters
