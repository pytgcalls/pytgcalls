from deprecation import deprecated

from ..video_parameters import VideoParameters
from ..video_quality import VideoQuality


@deprecated(
    deprecated_in='1.0.0.dev6',
    details='This class is no longer supported.'
            'Use pytgcalls.types.VideoParameters.from_quality instead.',
)
class HighQualityVideo(VideoParameters):
    def __init__(self):
        super().__init__(*VideoQuality.HD_720p.value)
