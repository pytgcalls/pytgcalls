from typing import Optional

from .input_audio_stream import InputAudioStream
from .input_video_stream import InputVideoStream


class InputStream:
    def __init__(
        self,
        stream_audio: InputAudioStream,
        stream_video: Optional[InputVideoStream] = None,
    ):
        self.stream_audio: InputAudioStream = stream_audio
        self.stream_video: Optional[InputVideoStream] = stream_video
