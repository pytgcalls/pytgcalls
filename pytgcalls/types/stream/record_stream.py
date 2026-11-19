from pathlib import Path

from ntgcalls import Format
from ntgcalls import MediaSource

from ...list_to_cmd import list_to_cmd
from ...media_devices.speaker_device import SpeakerDevice
from ...statictypes import statictypes
from ..raw.audio_parameters import AudioParameters
from ..raw.audio_stream import AudioStream
from ..raw.stream import Stream
from ..raw.video_parameters import VideoParameters
from ..raw.video_stream import VideoStream
from ..stream.audio_quality import AudioQuality
from ..stream.video_quality import VideoQuality


class RecordStream(Stream):
    @statictypes
    def __init__(
        self,
        audio: bool | str | Path | SpeakerDevice = False,
        audio_parameters: AudioParameters | AudioQuality = AudioQuality.HIGH,
        camera: bool | str | Path = False,
        screen: bool | str | Path = False,
        video_parameters: VideoParameters
        | VideoQuality = VideoQuality.HD_720p,
    ):
        raw_audio_parameters = (
            audio_parameters
            if isinstance(audio_parameters, AudioParameters)
            else AudioParameters(*audio_parameters.value)
            if isinstance(audio_parameters, AudioQuality)
            else ValueError('Invalid audio parameters')
        )
        raw_video_parameters = (
            video_parameters
            if isinstance(video_parameters, VideoParameters)
            else VideoParameters(*video_parameters.value)
            if isinstance(video_parameters, VideoQuality)
            else ValueError('Invalid video parameters')
        )
        super().__init__(
            microphone=self._get_audio_stream(audio, raw_audio_parameters),
            speaker=None,
            camera=self._get_video_stream(camera, raw_video_parameters),
            screen=self._get_video_stream(screen, raw_video_parameters),
        )

    @staticmethod
    def _get_audio_stream(audio, raw_audio_parameters):
        if isinstance(audio, bool) and audio:
            return AudioStream(
                media_source=MediaSource.EXTERNAL,
                path='',
                parameters=raw_audio_parameters,
            )
        if isinstance(audio, Path):
            audio = str(audio)
        if isinstance(audio, str) and Path(audio).suffix.lower() in (
            '.opus',
            '.ogg',
        ):
            return AudioStream(
                media_source=MediaSource.FILE,
                path=audio,
                parameters=raw_audio_parameters,
                format=Format.OGG,
            )
        if isinstance(audio, str):
            is_lossless = raw_audio_parameters.sample_rate > 48000
            commands = [
                'ffmpeg',
                '-y',
                '-loglevel',
                'quiet',
                '-f',
                's16le',
                '-ar',
                str(raw_audio_parameters.sample_rate),
                '-ac',
                str(raw_audio_parameters.channels),
                '-i',
                'pipe:0',
                '-codec:a',
                'flac' if is_lossless else 'libmp3lame',
                '-f',
                'flac' if is_lossless else 'mp3',
                '-flush_packets',
                '1',
                audio,
            ]
            return AudioStream(
                media_source=MediaSource.SHELL,
                path=list_to_cmd(commands),
                parameters=raw_audio_parameters,
            )
        if isinstance(audio, SpeakerDevice):
            return AudioStream(
                media_source=MediaSource.DEVICE,
                path=audio.metadata,
                parameters=raw_audio_parameters,
            )
        return None

    @staticmethod
    def _get_video_stream(video, raw_video_parameters):
        if isinstance(video, bool):
            return (
                VideoStream(
                    media_source=MediaSource.EXTERNAL,
                    path='',
                    parameters=VideoParameters(
                        width=-1,
                        height=-1,
                        frame_rate=0,
                    ),
                )
                if video
                else None
            )
        video = str(video)
        if Path(video).suffix.lower() == '.mkv':
            return VideoStream(
                media_source=MediaSource.FILE,
                path=video,
                parameters=raw_video_parameters,
                format=Format.MATROSKA,
            )
        commands = [
            'ffmpeg',
            '-y',
            '-loglevel',
            'quiet',
            '-f',
            'rawvideo',
            '-pix_fmt',
            'yuv420p',
            '-s',
            f'{raw_video_parameters.width}x{raw_video_parameters.height}',
            '-r',
            str(raw_video_parameters.frame_rate),
            '-i',
            'pipe:0',
            '-pix_fmt',
            'yuv420p',
            video,
        ]
        return VideoStream(
            media_source=MediaSource.SHELL,
            path=list_to_cmd(commands),
            parameters=raw_video_parameters,
            format=Format.I420,
        )
