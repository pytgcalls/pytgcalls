from ..audio_parameters import AudioParameters


class HighQualityAudio(AudioParameters):
    """High Audio Quality (48K of bitrate)

    Attributes:
        bitrate (``int``):
            Audio bitrate
    """

    def __init__(self):
        super().__init__(
            48000,
        )
