from typing import Optional

from deprecation import deprecated

from ....statictypes import statictypes
from ...raw import Stream
from .input_audio_stream import InputAudioStream
from .input_video_stream import InputVideoStream


@deprecated(
    deprecated_in='1.0.0.dev1',
    details='Use pytgcalls.types.Stream instead.',
)
class InputStream(Stream):
    @statictypes
    def __init__(
        self,
        stream_audio: Optional[InputAudioStream] = None,
        stream_video: Optional[InputVideoStream] = None,
        lip_sync: bool = False,
    ):
        super().__init__(stream_audio, stream_video)
        self.lip_sync = lip_sync
