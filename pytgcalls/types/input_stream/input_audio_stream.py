from ..py_object import PyObject
from .audio_parameters import AudioParameters


class InputAudioStream(PyObject):
    def __init__(
        self,
        path: str,
        parameters: AudioParameters = AudioParameters(),
        header_enabled: bool = False,
    ):
        self.path: str = path
        self.parameters: AudioParameters = parameters
        self.header_enabled: bool = header_enabled
