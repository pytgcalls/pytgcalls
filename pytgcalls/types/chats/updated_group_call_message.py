from ..chats import GroupCallMessage
from ..update import Update


class UpdatedGroupCallMessage(Update):
    def __init__(
        self,
        chat_id: int,
        action: GroupCallMessage.Action,
        message_id: int,
        message: GroupCallMessage | None = None,
    ):
        super().__init__(chat_id)
        self.action = action
        self.message_id = message_id
        self.message = message
