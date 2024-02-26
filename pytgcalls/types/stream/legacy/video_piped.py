from typing import Dict
from typing import Optional

from deprecation import deprecated

from ....statictypes import statictypes
from ...raw import VideoParameters
from ..media_stream import MediaStream


@deprecated(
    deprecated_in='1.1.0',
    details='Use pytgcalls.types.MediaStream instead.',
)
class VideoPiped(MediaStream):
    @statictypes
    def __init__(
        self,
        path: str,
        video_parameters: VideoParameters = VideoParameters(),
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
    ):
        super().__init__(
            media_path=path,
            video_parameters=video_parameters,
            audio_flags=MediaStream.IGNORE,
            video_flags=MediaStream.REQUIRED,
            headers=headers,
            ffmpeg_parameters=additional_ffmpeg_parameters,
        )
