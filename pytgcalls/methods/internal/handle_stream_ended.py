from ntgcalls import StreamDevice
from ntgcalls import StreamType

from ...scaffold import Scaffold
from ...types import Device
from ...types import StreamEnded


class HandleStreamEnded(Scaffold):
    async def _handle_stream_ended(
        self,
        chat_id: int,
        stream_type: StreamType,
        device: StreamDevice,
    ):
        await self._propagate(
            StreamEnded(
                chat_id,
                StreamEnded.Type.from_raw(stream_type),
                Device.from_raw(device),
            ),
            self,
        )
