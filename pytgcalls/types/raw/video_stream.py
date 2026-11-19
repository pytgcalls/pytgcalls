from ntgcalls import Format
from ntgcalls import MediaSource

from ...statictypes import statictypes
from ..py_object import PyObject
from .video_parameters import VideoParameters


class VideoStream(PyObject):
    @statictypes
    def __init__(
        self,
        media_source: MediaSource,
        path: str,
        parameters: VideoParameters = VideoParameters(),
        format: Format = Format.I420,
    ):
        self.media_source: MediaSource = media_source
        self.path: str = path
        self.parameters: VideoParameters = parameters
        self.format: Format = format
