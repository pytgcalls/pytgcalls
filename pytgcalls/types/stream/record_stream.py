from typing import Union

from ntgcalls import MediaSource

from .. import AudioQuality
from ..raw import AudioParameters
from ..raw.audio_stream import AudioStream
from ..raw.stream import Stream
from ..raw.video_parameters import VideoParameters
from ..raw.video_stream import VideoStream


class RecordStream(Stream):
    def __init__(
        self,
        audio: Union[bool, str] = False,
        audio_parameters: Union[
            AudioParameters,
            AudioQuality,
        ] = AudioQuality.HIGH,
        camera: bool = False,
        screen: bool = False,
    ):
        if isinstance(audio_parameters, AudioParameters):
            raw_audio_parameters = audio_parameters
        elif isinstance(audio_parameters, AudioQuality):
            raw_audio_parameters = AudioParameters(*audio_parameters.value)
        else:
            raise ValueError('Invalid audio parameters')

        microphone = None
        if isinstance(audio, bool) and audio:
            microphone = AudioStream(
                media_source=MediaSource.EXTERNAL,
                path='',
                parameters=raw_audio_parameters,
            )
        elif isinstance(audio, str):
            is_lossless = audio_parameters.bitrate > 48000
            commands = [
                'ffmpeg',
                '-loglevel',
                'quiet',
                '-f',
                's16le',
                '-ar',
                str(raw_audio_parameters.bitrate),
                '-ac',
                str(raw_audio_parameters.channels),
                '-i',
                'pipe:0',
                '-codec:a',
                'flac' if is_lossless else 'libmp3lame',
                audio,
            ]
            microphone = AudioStream(
                media_source=MediaSource.SHELL,
                path=' '.join(commands),
                parameters=raw_audio_parameters,
            )

        super().__init__(
            microphone=microphone,
            speaker=None,
            camera=None if not camera else VideoStream(
                media_source=MediaSource.EXTERNAL,
                path='',
                parameters=VideoParameters(
                    width=-1,
                    height=-1,
                    frame_rate=-1,
                ),
            ),
            screen=None if not screen else VideoStream(
                media_source=MediaSource.EXTERNAL,
                path='',
                parameters=VideoParameters(
                    width=-1,
                    height=-1,
                    frame_rate=-1,
                ),
            ),
        )
