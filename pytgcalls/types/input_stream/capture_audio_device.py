from ntgcalls import InputMode

from ...ffprobe import FFprobe
from ...media_devices.device_info import DeviceInfo
from .audio_parameters import AudioParameters
from .audio_stream import AudioStream
from .input_stream import Stream


class CaptureAudioDevice(Stream):
    def __init__(
        self,
        audio_info: DeviceInfo,
        audio_parameters: AudioParameters = AudioParameters(),
    ):
        self._audio_path: str = audio_info.build_ffmpeg_command()
        self.ffmpeg_parameters: str = audio_info.ffmpeg_parameters
        self.raw_headers = None
        super().__init__(
            AudioStream(
                InputMode.FFmpeg,
                f'device://{self._audio_path}',
                audio_parameters,
            ),
        )

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)
