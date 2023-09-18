from ntgcalls import InputMode

from ...ffmpeg import build_ffmpeg_command
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
        super().__init__(
            AudioStream(
                InputMode.Shell,
                build_ffmpeg_command(
                    '',
                    self._audio_path,
                    audio_parameters,
                    audio_info.ffmpeg_parameters,
                ),
                audio_parameters,
            ),
        )
