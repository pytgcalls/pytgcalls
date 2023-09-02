import deprecation
from ntgcalls import InputMode

from ... import __version__
from .audio_parameters import AudioParameters
from .audio_stream import AudioStream


@deprecation.deprecated(
    deprecated_in='1.0.0.dev1',
    current_version=__version__,
    details='Use pytgcalls.AudioStream instead.',
)
class InputAudioStream(AudioStream):
    def __init__(
        self,
        path: str,
        parameters: AudioParameters = AudioParameters(),
        header_enabled: bool = False,
    ):
        super().__init__(InputMode.File, path, parameters, header_enabled)
