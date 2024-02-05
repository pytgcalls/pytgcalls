from deprecation import deprecated

from ....media_devices import DeviceInfo
from ....statictypes import statictypes
from ...raw import AudioParameters
from ..media_stream import MediaStream


@deprecated(
    deprecated_in='1.1.0',
    details='Use pytgcalls.types.MediaStream instead.',
)
class CaptureAudioDevice(MediaStream):
    @statictypes
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
