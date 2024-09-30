from typing import Optional
from typing import Union

from ntgcalls import AudioDescription
from ntgcalls import MediaDescription
from ntgcalls import VideoDescription

from ...types.raw import AudioStream
from ...types.raw import VideoStream
from ...types.raw.stream import Stream
from ...types.stream.media_stream import MediaStream


class StreamParams:
    @staticmethod
    async def get_stream_params(stream: Optional[Stream]) -> MediaDescription:
        def parse_media_description(
            media: Optional[Union[AudioStream, VideoStream]],
        ) -> Optional[Union[AudioDescription, VideoDescription]]:
            if media is not None:
                if isinstance(media, AudioStream):
                    return AudioDescription(
                        input_mode=media.input_mode,
                        input=media.path,
                        sample_rate=media.parameters.bitrate,
                        bits_per_sample=16,
                        channel_count=media.parameters.channels,
                    )
                elif isinstance(media, VideoStream):
                    return VideoDescription(
                        input_mode=media.input_mode,
                        input=media.path,
                        width=media.parameters.width,
                        height=media.parameters.height,
                        fps=media.parameters.frame_rate,
                    )
            return None

        if stream is not None:
            if isinstance(stream, MediaStream):
                await stream.check_stream()

        return MediaDescription(
            microphone=parse_media_description(
                None if stream is None else stream.microphone,
            ),
            speaker=parse_media_description(
                None if stream is None else stream.speaker,
            ),
            camera=parse_media_description(
                None if stream is None else stream.camera,
            ),
            screen=parse_media_description(
                None if stream is None else stream.screen,
            ),
        )
