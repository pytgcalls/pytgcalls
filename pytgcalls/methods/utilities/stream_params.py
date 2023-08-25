import logging

from ntgcalls import AudioDescription, VideoDescription, MediaDescription
from pytgcalls.types import CaptureAudioDevice
from pytgcalls.types import CaptureVideoDesktop
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream import AudioVideoPiped
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream import VideoPiped
from pytgcalls.types.input_stream.audio_image_piped import AudioImagePiped

py_logger = logging.getLogger('pytgcalls')


class StreamParams:

    @staticmethod
    async def get_stream_params(stream: InputStream) -> MediaDescription:
        audio_description = None
        video_description = None

        raw_encoder = True
        # TODO CaptureAVDeviceDesktop ?
        if isinstance(
                stream,
                (AudioImagePiped, AudioPiped, AudioVideoPiped, VideoPiped, CaptureVideoDesktop, CaptureAudioDevice)
        ):
            await stream.check_pipe()
            raw_encoder = False

        if stream.stream_audio is not None:
            audio_description = AudioDescription(
                sampleRate=stream.stream_audio.parameters.bitrate,
                bitsPerSample=16,
                channelCount=stream.stream_audio.parameters.channels,
                path=stream.stream_audio.path,
            )

        if stream.stream_video is not None:
            if stream.stream_video.parameters.frame_rate % 5 != 0 and \
                    not isinstance(stream, AudioImagePiped):
                py_logger.warning(
                    'For better experience the '
                    'video frame rate must be a multiple of 5',
                )

            video_description = VideoDescription(
                width=stream.stream_video.parameters.width,
                height=stream.stream_video.parameters.height,
                fps=stream.stream_video.parameters.frame_rate,
                path=stream.stream_video.path
            )

        return MediaDescription(
            encoder='raw' if raw_encoder else 'ffmpeg',
            audio=audio_description,
            video=video_description
        )
