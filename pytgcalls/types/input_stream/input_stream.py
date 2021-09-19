from typing import Optional

from .input_audio_stream import InputAudioStream
from .input_video_stream import InputVideoStream


class InputStream:
    def __init__(
        self,
        stream_audio: Optional[InputAudioStream] = None,
        stream_video: Optional[InputVideoStream] = None,
        lip_sync: bool = False,
    ):
        self.stream_audio: Optional[InputAudioStream] = stream_audio
        self.stream_video: Optional[InputVideoStream] = stream_video
        self.lip_sync = lip_sync
