from typing import Optional, Any

from pytgcalls.types.update import Update


class RawCallUpdate(Update):
    ACCEPTED = 1 << 0
    CONFIRMED = 1 << 1
    REQUESTED = 1 << 2
    UPDATED_CALL = ACCEPTED | CONFIRMED
    SIGNALING_DATA = 1 << 3

    def __init__(
        self,
        chat_id: int,
        status: int,
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
