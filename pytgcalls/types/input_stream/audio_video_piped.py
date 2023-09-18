from typing import Dict
from typing import Optional

from ntgcalls import InputMode

from ...ffmpeg import build_ffmpeg_command
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
        super().__init__(
            AudioStream(
                InputMode.Shell,
                build_ffmpeg_command(
                    additional_ffmpeg_parameters,
                    self._path,
                    audio_parameters,
                    [],
                    headers,
                ),
                audio_parameters
            ),
            VideoStream(
                InputMode.Shell,
                build_ffmpeg_command(
                    additional_ffmpeg_parameters,
                    self._path,
                    video_parameters,
                    [],
                    headers,
                ),
                video_parameters
            ),
        )
