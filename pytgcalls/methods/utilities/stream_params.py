from pathlib import Path
from typing import Optional
from typing import Union

from ntgcalls import AudioDescription
from ntgcalls import MediaDescription
from ntgcalls import VideoDescription

from ...media_devices.input_device import InputDevice
from ...media_devices.speaker_device import SpeakerDevice
from ...types import RecordStream
from ...types.raw import AudioStream
from ...types.raw import Stream
from ...types.raw import VideoStream
from ...types.stream.media_stream import MediaStream


class StreamParams:
    @staticmethod
    async def get_stream_params(
        stream: Optional[Union[str, Path, InputDevice, Stream]],
    ) -> MediaDescription:
        if stream is not None:
            if isinstance(stream, (str, Path, InputDevice)):
                stream = MediaStream(stream)
            if isinstance(stream, MediaStream):
                await stream.check_stream()
            elif isinstance(stream, RecordStream):
                raise ValueError(
                    'Stream should be an instance of '
                    'MediaStream or a raw Stream',
                )

        return StreamParams._parse_stream_description(stream)

    @staticmethod
    def _parse_media_description(
        media: Optional[Union[AudioStream, VideoStream]],
    ) -> Optional[Union[AudioDescription, VideoDescription]]:
        if media is not None:
            if isinstance(media, AudioStream):
                return AudioDescription(
                    media_source=media.media_source,
                    input=media.path,
                    sample_rate=media.parameters.bitrate,
                    channel_count=media.parameters.channels,
                )
            elif isinstance(media, VideoStream):
                return VideoDescription(
                    media_source=media.media_source,
                    input=media.path,
                    width=media.parameters.width,
                    height=media.parameters.height,
                    fps=media.parameters.frame_rate,
                )
        return None

    @staticmethod
    def _parse_stream_description(
        stream: Optional[Stream],
    ) -> MediaDescription:
        return MediaDescription(
            microphone=StreamParams._parse_media_description(
                None if stream is None else stream.microphone,
            ),
            speaker=StreamParams._parse_media_description(
                None if stream is None else stream.speaker,
            ),
            camera=StreamParams._parse_media_description(
                None if stream is None else stream.camera,
            ),
            screen=StreamParams._parse_media_description(
                None if stream is None else stream.screen,
            ),
        )

    @staticmethod
    async def get_record_params(
        stream: Optional[Union[str, Path, Stream, SpeakerDevice]],
    ) -> MediaDescription:
        if stream is not None:
            if isinstance(stream, (str, Path, SpeakerDevice)):
                stream = RecordStream(stream)
            if isinstance(stream, MediaStream):
                raise ValueError(
                    'Stream should be an instance of '
                    'RecordStream or a raw Stream',
                )
        return StreamParams._parse_stream_description(stream)  # type: ignore
