from typing import Dict
from typing import Optional

from deprecation import deprecated

from .media_stream import MediaStream
from .video_parameters import VideoParameters


@deprecated(
    deprecated_in='1.1.0',
    details='This class is no longer supported.'
            'Use pytgcalls.types.input_stream.MediaStream instead.',
)
class VideoPiped(MediaStream):
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
            additional_ffmpeg_parameters=additional_ffmpeg_parameters,
        )
