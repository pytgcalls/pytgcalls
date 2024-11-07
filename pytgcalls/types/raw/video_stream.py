from ntgcalls import MediaSource

from ...statictypes import statictypes
from .video_parameters import VideoParameters


class VideoStream:
    @statictypes
    def __init__(
        self,
        media_source: MediaSource,
        path: str,
        parameters: VideoParameters = VideoParameters(),
    ):
        self.media_source: MediaSource = media_source
        self.path: str = path
        self.parameters: VideoParameters = parameters
