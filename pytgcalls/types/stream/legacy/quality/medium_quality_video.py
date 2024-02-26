from deprecation import deprecated

from .... import VideoQuality
from ....raw import VideoParameters


@deprecated(
    deprecated_in='1.0.0.dev6',
    details='Use pytgcalls.types.VideoParameters.from_quality instead.',
)
class MediumQualityVideo(VideoParameters):
    def __init__(self):
        super().__init__(*VideoQuality.SD_360p.value)
