from typing import Dict
from typing import Optional

from deprecation import deprecated

from .audio_parameters import AudioParameters
from .media_stream import MediaStream
from .video_parameters import VideoParameters


@deprecated(
    deprecated_in='1.1.0',
    details='This class is no longer supported.'
            'Use pytgcalls.types.input_stream.MediaStream instead.',
)
class AudioImagePiped(MediaStream):
    def __init__(
        self,
        audio_path: str,
        image_path: str,
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
    ):
        super().__init__(
            media_path=image_path,
            audio_parameters=audio_parameters,
            video_parameters=video_parameters,
            audio_path=audio_path,
            audio_flags=MediaStream.REQUIRED,
            video_flags=MediaStream.REQUIRED,
            headers=headers,
            additional_ffmpeg_parameters=additional_ffmpeg_parameters,
        )
