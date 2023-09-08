from ..py_object import PyObject


class AudioParameters(PyObject):
    def __init__(
        self,
        bitrate: int = 48000,
        channels: int = 2,
    ):
        self.bitrate: int = 48000 if bitrate > 48000 else bitrate
        self.channels: int = 2 if channels > 2 else channels
