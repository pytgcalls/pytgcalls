from ..audio_parameters import AudioParameters


class MediumQualityAudio(AudioParameters):
    """Medium Audio Quality (36K of bitrate)

    Attributes:
        bitrate (``int``):
            Audio bitrate
    """

    def __init__(self):
        super().__init__(
            36000,
        )
