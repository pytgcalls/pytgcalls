from ...statictypes import statictypes
from ..py_object import PyObject
from ..stream.audio_quality import AudioQuality


class AudioParameters(PyObject):
    @statictypes
    def __init__(
        self,
        sample_rate: int = 48000,
        channels: int = 1,
        bitrate: int | None = None,
    ):
        max_rate, max_chan = max(
            AudioQuality,
            key=lambda x: x.value[0],
        ).value[:2]
        self.sample_rate: int = min(sample_rate, max_rate)
        self.channels: int = min(channels, max_chan)
        self.bitrate: int | None = None
        if bitrate is not None:
            self.bitrate = max(6000, min(bitrate, 510000))
