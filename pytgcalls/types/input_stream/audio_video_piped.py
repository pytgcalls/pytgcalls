from .video_parameters import VideoParameters
from .input_audio_stream import InputAudioStream
from .input_video_stream import InputVideoStream
from .audio_parameters import AudioParameters
from .input_stream import InputStream
from ...custom_fifo.ffprobe import FFprobe


class AudioVideoPiped(InputStream):
    def __init__(
        self,
        path: str,
        audio_parameters: AudioParameters = AudioParameters(),
    ):
        self._path = path
        super().__init__(
            InputAudioStream(
                f'fifo://{path}',
                audio_parameters,
            ),
            InputVideoStream(
                f'fifo://{path}',
            )
        )

    async def check_pipe(self):
        await FFprobe.check_file(self._path)
