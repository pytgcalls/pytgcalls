from typing import Any

from ..update import Update


class ChatUpdate(Update):
    KICKED = 1
    LEFT_GROUP = 2
    CLOSED_VOICE_CHAT = 4
    INVITED_VOICE_CHAT = 8
    LEFT_VOICE_CHAT = KICKED | LEFT_GROUP | CLOSED_VOICE_CHAT

    def __init__(
        self,
        chat_id: int,
        status: int,
        action: Any = None,
    ):
        super().__init__(chat_id)
        self.status: int = status
        self.action = action
