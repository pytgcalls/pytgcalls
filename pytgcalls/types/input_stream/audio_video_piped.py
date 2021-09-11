from math import ceil

from ...exceptions import InvalidVideoProportion
from ...ffprobe import FFprobe
from .audio_parameters import AudioParameters
from .input_audio_stream import InputAudioStream
from .input_stream import InputStream
from .input_video_stream import InputVideoStream
from .video_parameters import VideoParameters


class AudioVideoPiped(InputStream):
    def __init__(
        self,
        path: str,
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
    ):
        self._path = path
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

    async def check_pipe(self):
        dest_width, dest_height = await FFprobe.check_file(self._path, True)
        height = self.stream_video.parameters.height
        if dest_height < height:
            raise InvalidVideoProportion(
                'Destination height is greater than the original height',
            )
        ratio = (dest_width / dest_height)
        self.stream_video.parameters.width = ceil(height * ratio)
        self.stream_video.parameters.height = height
