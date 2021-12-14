from typing import Dict
from typing import Optional

from ...ffprobe import FFprobe
from .audio_parameters import AudioParameters
from .input_audio_stream import InputAudioStream
from .input_stream import InputStream


class AudioPiped(InputStream):
    """The audio only stream piped descriptor

    Attributes:
        ffmpeg_parameters (``str``):
            FFMpeg additional parameters
        lip_sync (``bool``):
            Lip Sync mode
        raw_headers (``str``):
            Headers of http the connection
        stream_audio (:obj:`~pytgcalls.types.InputAudioStream()`):
            Input Audio Stream Descriptor
        stream_video (:obj:`~pytgcalls.types.InputVideoStream()`):
            Input Video Stream Descriptor

    Parameters:
        path (``str``):
            The audio file path
        audio_parameters (:obj:`~pytgcalls.types.AudioParameters()`):
            The audio parameters of the stream, can be used also
            :obj:`~pytgcalls.types.HighQualityAudio()`,
            :obj:`~pytgcalls.types.MediumQualityAudio()` or
            :obj:`~pytgcalls.types.LowQualityAudio()`
        headers (``Dict[str, str]``, **optional**):
            Headers of http the connection
        additional_ffmpeg_parameters (``str``, **optional**):
            FFMpeg additional parameters
    """

    def __init__(
        self,
        path: str,
        audio_parameters: AudioParameters = AudioParameters(),
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
        )

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)

    async def check_pipe(self):
        header = await FFprobe.check_file(
            self._path,
            needed_audio=True,
            needed_video=False,
            headers=self.raw_headers,
        )
        self.stream_audio.header_enabled = header
