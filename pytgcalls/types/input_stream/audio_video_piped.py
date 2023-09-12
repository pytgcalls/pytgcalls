from typing import Dict
from typing import Optional

from ntgcalls import InputMode

from ...ffprobe import FFprobe
from .audio_parameters import AudioParameters
from .audio_stream import AudioStream
from .input_stream import Stream
from .video_parameters import VideoParameters
from .video_stream import VideoStream


class AudioVideoPiped(Stream):
    def __init__(
        self,
        path: str,
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
    ):
        self._path = path
        self.ffmpeg_parameters = additional_ffmpeg_parameters
        self.raw_headers = headers
        super().__init__(
            AudioStream(
                InputMode.FFmpeg,
                f'fifo://{path}',
                audio_parameters,
            ),
            VideoStream(
                InputMode.FFmpeg,
                f'fifo://{path}',
                video_parameters,
            ),
        )
        self.lip_sync = True

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)
