from ..py_object import PyObject
from .audio_parameters import AudioParameters


class InputAudioStream(PyObject):
    def __init__(
        self,
        path: str,
        parameters: AudioParameters = AudioParameters(),
    ):
        self.path: str = path
        self.parameters: AudioParameters = parameters
