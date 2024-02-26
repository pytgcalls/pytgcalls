from deprecation import deprecated

from ....media_devices import DeviceInfo
from ....media_devices import ScreenInfo
from ....statictypes import statictypes
from ...raw import AudioParameters
from ...raw import VideoParameters
from ..media_stream import MediaStream


@deprecated(
    deprecated_in='1.1.0',
    details='Use pytgcalls.types.MediaStream instead.',
)
class CaptureAVDeviceDesktop(MediaStream):
    @statictypes
    def __init__(
        self,
        audio_info: DeviceInfo,
        screen_info: ScreenInfo,
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
    ):
        super().__init__(
            media_path=screen_info,
            audio_parameters=audio_parameters,
            video_parameters=video_parameters,
            audio_path=audio_info,
            audio_flags=MediaStream.REQUIRED,
            video_flags=MediaStream.REQUIRED,
        )
