import asyncio

from ntgcalls import StreamType

from ...scaffold import Scaffold
from ...types.stream import StreamAudioEnded
from ...types.stream import StreamVideoEnded


class StreamEndedHandler(Scaffold):
    def _stream_ended_handler(
        self,
        chat_id: int,
        stream: StreamType,
    ):
        async def async_stream_ended_handler():
            await self._on_event_update.propagate(
                'STREAM_END_HANDLER',
                self,
                StreamAudioEnded(
                    chat_id,
                ) if stream.Audio else StreamVideoEnded(chat_id),
            )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_stream_ended_handler())
