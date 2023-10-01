from deprecation import deprecated

from ..audio_parameters import AudioParameters
from ..audio_quality import AudioQuality


@deprecated(
    deprecated_in='1.0.0.dev6',
    details='This class is no longer supported.'
            'Use pytgcalls.types.AudioParameters.from_quality instead.',
)
class HighQualityAudio(AudioParameters):
    def __init__(self):
        super().__init__(*AudioQuality.HIGH.value)
