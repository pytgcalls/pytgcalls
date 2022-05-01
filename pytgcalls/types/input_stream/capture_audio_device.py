from ...ffprobe import FFprobe
from ...media_devices.device_info import DeviceInfo
from .audio_parameters import AudioParameters
from .input_stream import InputAudioStream
from .input_stream import InputStream


class CaptureAudioDevice(InputStream):
    """Capture video from Screen and Audio from device

    Attributes:
        stream_audio (:obj:`~pytgcalls.types.InputAudioStream()`):
            Input Audio Stream Descriptor
        stream_video (:obj:`~pytgcalls.types.InputVideoStream()`):
            Input Video Stream Descriptor
    Parameters:
        audio_info (:obj: `~pytgcalls.media_devices.DeviceInfo()`):
            The audio device capturing params
        audio_parameters (:obj:`~pytgcalls.types.AudioParameters()`):
            The audio parameters of the stream, can be used also
            :obj:`~pytgcalls.types.HighQualityAudio()`,
            :obj:`~pytgcalls.types.MediumQualityAudio()` or
            :obj:`~pytgcalls.types.LowQualityAudio()`
    """

    def __init__(
        self,
        audio_info: DeviceInfo,
        audio_parameters: AudioParameters = AudioParameters(),
    ):
        self._audio_path: str = audio_info.buildFFMpegCommand()
        self.ffmpeg_parameters: str = audio_info.ffmpeg_parameters
        self.raw_headers = None
        super().__init__(
            InputAudioStream(
                f'device://{self._audio_path}',
                audio_parameters,
            ),
        )

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)

    async def check_pipe(self):
        pass
