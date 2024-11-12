from enum import auto

from ntgcalls import StreamType

from ...types.update import Update
from ..flag import Flag
from .device import Device


class StreamEnded(Update):

    class Type(Flag):
        AUDIO = auto()
        VIDEO = auto()

        @staticmethod
        def from_raw(kind: StreamType):
            if kind == StreamType.AUDIO:
                return StreamEnded.Type.AUDIO
            if kind == StreamType.VIDEO:
                return StreamEnded.Type.VIDEO
            return None

    def __init__(
        self,
        chat_id: int,
        stream_type: Type,
        device: Device,
    ):
        super().__init__(chat_id)
        self.stream_type = stream_type
        self.device = device
