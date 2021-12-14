from ..py_object import PyObject
from .audio_parameters import AudioParameters


class InputAudioStream(PyObject):
    """The raw audio stream (PCM16L) descriptor

    Attributes:
        path (``str``):
            The audio file path
        parameters (:obj:`~pytgcalls.types.AudioParameters()`):
            The audio parameters of the stream

    Parameters:
        path (``str``):
            The audio file path (PCM16L format only)
        parameters (:obj:`~pytgcalls.types.AudioParameters()`):
            The audio parameters of the stream, can be used also
            :obj:`~pytgcalls.types.HighQualityAudio()`,
            :obj:`~pytgcalls.types.MediumQualityAudio()` or
            :obj:`~pytgcalls.types.LowQualityAudio()`
    """

    def __init__(
        self,
        path: str,
        parameters: AudioParameters = AudioParameters(),
        header_enabled: bool = False,
    ):
        self.path: str = path
        self.parameters: AudioParameters = parameters
        self.header_enabled: bool = header_enabled
