from typing import Optional

from ..py_object import PyObject
from .input_audio_stream import AudioStream
from .video_stream import VideoStream


class InputStream(PyObject):
    """The streams descriptor

    Attributes:
        lip_sync (``bool``):
            Lip Sync mode
        stream_audio (:obj:`~pytgcalls.types.InputAudioStream()`):
            Input Audio Stream Descriptor
        stream_video (:obj:`~pytgcalls.types.InputVideoStream()`):
            Input Video Stream Descriptor

    Parameters:
        stream_audio (:obj:`~pytgcalls.types.InputAudioStream()`):
            Audio File Descriptor
        stream_video (:obj:`~pytgcalls.types.InputVideoStream()`):
            Video File Descriptor
        lip_sync (``bool``, **optional**):
            Lip Sync mode
    """

    def __init__(
        self,
        stream_audio: Optional[AudioStream] = None,
        stream_video: Optional[VideoStream] = None,
        lip_sync: bool = False,
    ):
        self.stream_audio: Optional[AudioStream] = stream_audio
        self.stream_video: Optional[VideoStream] = stream_video
        self.lip_sync = lip_sync
