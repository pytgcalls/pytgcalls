from typing import Dict
from typing import Optional

from ntgcalls import InputMode

from ...ffmpeg import build_command
from ...ffmpeg import check_stream
from .audio_parameters import AudioParameters
from .audio_stream import AudioStream
from .smart_stream import SmartStream


class AudioPiped(SmartStream):
    def __init__(
        self,
        path: str,
        audio_parameters: AudioParameters = AudioParameters(),
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
    ):
        self._path = path
        self._audio_data = (
            additional_ffmpeg_parameters,
            self._path,
            audio_parameters,
            [],
            headers,
        )
        super().__init__(
            AudioStream(
                InputMode.Shell,
                ' '.join(
                    build_command(
                        'ffmpeg',
                        *self._audio_data,
                    ),
                ),
                audio_parameters,
            ),
        )

    async def check_stream(self):
        await check_stream(
            *self._audio_data,
        )
