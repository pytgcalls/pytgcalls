from ntgcalls import StreamDevice
from ntgcalls import StreamType

from ...types.update import Update


class StreamEnded(Update):
    def __init__(
        self,
        chat_id: int,
        stream_type: StreamType,
        device: StreamDevice,
    ):
        super().__init__(chat_id)
        self.stream_type = stream_type
        self.device = device
