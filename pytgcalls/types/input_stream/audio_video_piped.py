from math import gcd
from typing import Optional, Dict

from ...exceptions import InvalidVideoProportion
from ...ffprobe import FFprobe
from .audio_parameters import AudioParameters
from .input_audio_stream import InputAudioStream
from .input_stream import InputStream
from .input_video_stream import InputVideoStream
from .quality import HighQualityVideo
from .quality import LowQualityVideo
from .quality import MediumQualityVideo
from .video_parameters import VideoParameters


class AudioVideoPiped(InputStream):
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
            InputAudioStream(
                f'fifo://{path}',
                audio_parameters,
            ),
            InputVideoStream(
                f'fifo://{path}',
                video_parameters,
            ),
        )

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)

    async def check_pipe(self):
        dest_width, dest_height = await FFprobe.check_file(
            self._path,
            True,
            self.raw_headers,
        )

        def resize_ratio(w, h, factor):
            if w > h:
                rescaling = ((1280 if w > 1280 else w) * 100) / w
            else:
                rescaling = ((720 if h > 720 else h) * 100) / h
            h = round((h * rescaling) / 100)
            w = round((w * rescaling) / 100)
            divisor = gcd(w, h)
            ratio_w = w / divisor
            ratio_h = h / divisor
            factor = (divisor * factor) / 100
            return round(ratio_w * factor), round(ratio_h * factor)
        height = self.stream_video.parameters.height
        width = self.stream_video.parameters.width
        if isinstance(
            self.stream_video.parameters,
            HighQualityVideo,
        ):
            width, height = resize_ratio(dest_width, dest_height, 100)
        if isinstance(
            self.stream_video.parameters,
            MediumQualityVideo,
        ):
            width, height = resize_ratio(dest_width, dest_height, 66.69)
        if isinstance(
            self.stream_video.parameters,
            LowQualityVideo,
        ):
            width, height = resize_ratio(dest_width, dest_height, 50)
        if dest_height < height:
            raise InvalidVideoProportion(
                'Destination height is greater than the original height',
            )
        self.stream_video.parameters.width = width - 1 if width % 2 else width
        self.stream_video.parameters.height = height
