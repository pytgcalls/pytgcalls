import logging
from typing import Optional

from ntgcalls import AudioDescription
from ntgcalls import MediaDescription
from ntgcalls import VideoDescription

from pytgcalls.types.input_stream.audio_image_piped import AudioImagePiped
from pytgcalls.types.input_stream.smart_stream import SmartStream
from pytgcalls.types.input_stream.stream import Stream

py_logger = logging.getLogger('pytgcalls')


class StreamParams:
    @staticmethod
    async def get_stream_params(stream: Optional[Stream]) -> MediaDescription:
        audio_description = None
        video_description = None

        if stream is not None:
            if isinstance(stream, SmartStream):
                await stream.check_stream()

            if stream.stream_audio is not None:
                audio_description = AudioDescription(
                    input_mode=stream.stream_audio.input_mode,
                    input=stream.stream_audio.path,
                    sample_rate=stream.stream_audio.parameters.bitrate,
                    bits_per_sample=16,
                    channel_count=stream.stream_audio.parameters.channels,
                )

            if stream.stream_video is not None:
                if stream.stream_video.parameters.frame_rate % 5 != 0 and \
                        not isinstance(stream, AudioImagePiped):
                    py_logger.warning(
                        'For better experience the '
                        'video frame rate must be a multiple of 5',
                    )

                video_description = VideoDescription(
                    input_mode=stream.stream_video.input_mode,
                    input=stream.stream_video.path,
                    width=stream.stream_video.parameters.width,
                    height=stream.stream_video.parameters.height,
                    fps=stream.stream_video.parameters.frame_rate,
                )

        return MediaDescription(
            audio=audio_description,
            video=video_description,
        )
