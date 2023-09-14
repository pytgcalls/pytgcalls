from typing import Dict
from typing import Optional

from ntgcalls import InputMode

from ...ffprobe import FFprobe
from ...methods.utilities import ffmpeg_tools
from .audio_parameters import AudioParameters
from .audio_stream import AudioStream
from .input_stream import Stream


class AudioPiped(Stream):
    def __init__(
        self,
        path: str,
        audio_parameters: AudioParameters = AudioParameters(),
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
    ):
        self._path = path
        self.ffmpeg_parameters = additional_ffmpeg_parameters
        self.raw_headers = headers
        super().__init__(
            AudioStream(
                InputMode.Shell,
                ffmpeg_tools.build_ffmpeg_command(
                    self.ffmpeg_parameters,
                    self._path,
                    'audio',
                    audio_parameters,
                ),
                audio_parameters,
            ),
        )

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)
