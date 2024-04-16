from enum import auto
from enum import Flag
from typing import Optional

from pytgcalls.types.update import Update


class RawCallUpdate(Update):
    class Type(Flag):
        ACCEPTED = auto()
        CONFIRMED = auto()
        REQUESTED = auto()
        SIGNALING_DATA = auto()
        UPDATED_CALL = ACCEPTED | CONFIRMED

    def __init__(
        self,
        chat_id: int,
        status: Type,
        g_a_or_b: Optional[bytes] = None,
        protocol=None,
        fingerprint: int = 0,
        signaling_data: Optional[bytes] = None,
    ):
        super().__init__(chat_id)
        self.chat_id = chat_id
        self.status = status
        self.g_a_or_b = g_a_or_b
        self.fingerprint = fingerprint
        self.protocol = protocol
        self.signaling_data = signaling_data
