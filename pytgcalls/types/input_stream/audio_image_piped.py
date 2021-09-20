from typing import Dict
from typing import Optional

from ...ffprobe import FFprobe
from .audio_parameters import AudioParameters
from .input_audio_stream import InputAudioStream
from .input_stream import InputStream
from .input_video_stream import InputVideoStream
from .video_parameters import VideoParameters
from .video_tools import check_video_params


class AudioImagePiped(InputStream):
    def __init__(
        self,
        audio_path: str,
        image_path: str,
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
    ):
        self._image_path = image_path
        self._audio_path = audio_path
        self.ffmpeg_parameters = additional_ffmpeg_parameters
        self.raw_headers = headers
        video_parameters.frame_rate = 1
        super().__init__(
            InputAudioStream(
                f'fifo://{audio_path}',
                audio_parameters,
            ),
            InputVideoStream(
                f'fifo://image:{image_path}',
                video_parameters,
            ),
        )

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)

    async def check_pipe(self):
        dest_width, dest_height = await FFprobe.check_file(
            self._image_path,
            needed_audio=False,
            needed_video=True,
            headers=self.raw_headers,
        )
        await FFprobe.check_file(
            self._audio_path,
            needed_audio=True,
            needed_video=False,
            headers=self.raw_headers,
        )
        width, height = check_video_params(
            self.stream_video.parameters,
            dest_width,
            dest_height,
        )
        self.stream_video.parameters.width = width
        self.stream_video.parameters.height = height
