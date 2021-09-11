from ...ffprobe import FFprobe
from .audio_parameters import AudioParameters
from .input_audio_stream import InputAudioStream
from .input_stream import InputStream


class AudioPiped(InputStream):
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
        )

    async def check_pipe(self):
        await FFprobe.check_file(self._path)
