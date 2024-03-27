from typing import Any

from ..update import Update


class ChatUpdate(Update):
    KICKED = 1 << 0
    LEFT_GROUP = 1 << 1
    CLOSED_VOICE_CHAT = 1 << 2
    INVITED_VOICE_CHAT = 1 << 3
    DISCARDED_CALL = 1 << 4
    INCOMING_CALL = 1 << 5
    LEFT_CALL = KICKED | LEFT_GROUP | CLOSED_VOICE_CHAT | DISCARDED_CALL

    def __init__(
        self,
        chat_id: int,
        status: int,
        action: Any = None,
    ):
        super().__init__(chat_id)
        self.status: int = status
        self.action = action
