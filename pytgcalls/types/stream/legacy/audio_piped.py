from typing import Dict
from typing import Optional

from deprecation import deprecated

from ....statictypes import statictypes
from ...raw import AudioParameters
from ..media_stream import MediaStream


@deprecated(
    deprecated_in='1.1.0',
    details='Use pytgcalls.types.MediaStream instead.',
)
class AudioPiped(MediaStream):
    @statictypes
    def __init__(
        self,
        path: str,
        audio_parameters: AudioParameters = AudioParameters(),
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
    ):
        super().__init__(
            media_path=path,
            audio_parameters=audio_parameters,
            audio_flags=MediaStream.REQUIRED,
            video_flags=MediaStream.IGNORE,
            headers=headers,
            ffmpeg_parameters=additional_ffmpeg_parameters,
        )
