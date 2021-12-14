from ..audio_parameters import AudioParameters


class LowQualityAudio(AudioParameters):
    """Low Audio Quality (24K of bitrate)

    Attributes:
        bitrate (``int``):
            Audio bitrate
    """

    def __init__(self):
        super().__init__(
            24000,
        )
