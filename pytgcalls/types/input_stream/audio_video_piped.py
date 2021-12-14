from typing import Dict
from typing import Optional

from ...ffprobe import FFprobe
from .audio_parameters import AudioParameters
from .input_audio_stream import InputAudioStream
from .input_stream import InputStream
from .input_video_stream import InputVideoStream
from .video_parameters import VideoParameters
from .video_tools import check_video_params


class AudioVideoPiped(InputStream):
    """The audio/video stream piped descriptor

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
            The audio-video (Like MP4 or etc) file path
        audio_parameters (:obj:`~pytgcalls.types.AudioParameters()`):
            The audio parameters of the stream, can be used also
            :obj:`~pytgcalls.types.HighQualityAudio()`,
            :obj:`~pytgcalls.types.MediumQualityAudio()` or
            :obj:`~pytgcalls.types.LowQualityAudio()`
        video_parameters (:obj:`~pytgcalls.types.VideoParameters()`):
            The video parameters of the stream, can be used also
            :obj:`~pytgcalls.types.HighQualityVideo()`,
            :obj:`~pytgcalls.types.MediumQualityVideo()` or
            :obj:`~pytgcalls.types.LowQualityVideo()`
        headers (``Dict[str, str]``, **optional**):
            Headers of http the connection
        additional_ffmpeg_parameters (``str``, **optional**):
            FFMpeg additional parameters
    """

    def __init__(
        self,
        path: str,
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
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
            InputVideoStream(
                f'fifo://{path}',
                video_parameters,
            ),
        )
        self.lip_sync = True

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)

    async def check_pipe(self):
        dest_width, dest_height, header = await FFprobe.check_file(
            self._path,
            needed_audio=True,
            needed_video=True,
            headers=self.raw_headers,
        )
        width, height = check_video_params(
            self.stream_video.parameters,
            dest_width,
            dest_height,
        )
        self.stream_video.header_enabled = header
        self.stream_audio.header_enabled = header
        self.stream_video.parameters.width = width
        self.stream_video.parameters.height = height
