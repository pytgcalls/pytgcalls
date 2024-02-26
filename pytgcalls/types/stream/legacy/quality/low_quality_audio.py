from deprecation import deprecated

from .... import AudioQuality
from ....raw import AudioParameters


@deprecated(
    deprecated_in='1.0.0.dev6',
    details='Use pytgcalls.types.AudioParameters.from_quality instead.',
)
class LowQualityAudio(AudioParameters):
    def __init__(self):
        super().__init__(*AudioQuality.LOW.value)
