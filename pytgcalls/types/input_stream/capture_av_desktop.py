from typing import Dict
from typing import Optional

from ntgcalls import InputMode

from ...ffprobe import FFprobe
from ...media_devices.screen_info import ScreenInfo
from .audio_parameters import AudioParameters
from .audio_stream import AudioStream
from .input_stream import InputStream
from .video_parameters import VideoParameters
from .video_stream import VideoStream


class CaptureAVDesktop(InputStream):
    def __init__(
        self,
        audio_path: str,
        screen_info: ScreenInfo,
        headers: Optional[Dict[str, str]] = None,
        additional_ffmpeg_parameters: str = '',
        audio_parameters: AudioParameters = AudioParameters(),
        video_parameters: VideoParameters = VideoParameters(),
    ):
        self._audio_path = audio_path
        self.audio_ffmpeg: str = additional_ffmpeg_parameters
        self._video_path = screen_info.build_ffmpeg_command(
            video_parameters.frame_rate,
        )
        self.video_ffmpeg: str = screen_info.ffmpeg_parameters
        self.raw_headers = headers
        super().__init__(
            AudioStream(
                InputMode.FFmpeg,
                f'fifo://{self._audio_path}',
                audio_parameters,
            ),
            VideoStream(
                InputMode.FFmpeg,
                f'screen://{self._video_path}',
                video_parameters,
            ),
        )

    @property
    def headers(self):
        return FFprobe.ffmpeg_headers(self.raw_headers)

    async def check_pipe(self):
        header = await FFprobe.check_file(
            self._audio_path,
            needed_audio=True,
            needed_video=False,
            needed_image=False,
            headers=self.raw_headers,
        )
        self.stream_audio.header_enabled = header
