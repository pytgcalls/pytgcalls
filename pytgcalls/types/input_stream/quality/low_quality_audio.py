from ..audio_parameters import AudioParameters


class LowQualityAudio(AudioParameters):

    def __init__(self):
        super().__init__(
            24000,
        )
