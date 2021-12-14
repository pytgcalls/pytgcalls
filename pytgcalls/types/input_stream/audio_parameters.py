from ..py_object import PyObject


class AudioParameters(PyObject):
    """Audio parameters of the stream

    Attributes:
        bitrate (``int``):
            Audio bitrate

    Parameters:
        bitrate (``int``):
            Audio bitrate (0 - 48000 max
            allowed by Telegram)
    """

    def __init__(
        self,
        bitrate: int = 48000,
    ):
        self.bitrate: int = 48000 if bitrate > 48000 else bitrate
