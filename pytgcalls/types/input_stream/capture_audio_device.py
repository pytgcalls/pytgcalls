from deprecation import deprecated

from ...media_devices.device_info import DeviceInfo
from .audio_parameters import AudioParameters
from .media_stream import MediaStream


@deprecated(
    deprecated_in='1.1.0',
    details='This class is no longer supported.'
            'Use pytgcalls.types.input_stream.MediaStream instead.',
)
class CaptureAudioDevice(MediaStream):
    def __init__(
        self,
        audio_info: DeviceInfo,
        audio_parameters: AudioParameters = AudioParameters(),
    ):
        super().__init__(
            media_path=audio_info,
            audio_parameters=audio_parameters,
            audio_flags=MediaStream.REQUIRED,
            video_flags=MediaStream.IGNORE,
        )
