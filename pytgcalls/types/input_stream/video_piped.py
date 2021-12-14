from typing import Dict
from typing import Optional

from ...ffprobe import FFprobe
from .input_stream import InputStream
from .input_video_stream import InputVideoStream
from .video_parameters import VideoParameters
from .video_tools import check_video_params


class VideoPiped(InputStream):
    """The video only stream piped descriptor

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
            The video file path
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
        video_parameters: VideoParameters = VideoParameters(),
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
    ):
        self._path = path
        self.ffmpeg_parameters = additional_ffmpeg_parameters
        self.raw_headers = headers
        super().__init__(
            stream_video=InputVideoStream(
                f'fifo://{path}',
                video_parameters,
            ),
        )

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)

    async def check_pipe(self):
        dest_width, dest_height, header = await FFprobe.check_file(
            self._path,
            needed_audio=False,
            needed_video=True,
            headers=self.raw_headers,
        )
        width, height = check_video_params(
            self.stream_video.parameters,
            dest_width,
            dest_height,
        )
        self.stream_video.header_enabled = header
        self.stream_video.parameters.width = width
        self.stream_video.parameters.height = height
