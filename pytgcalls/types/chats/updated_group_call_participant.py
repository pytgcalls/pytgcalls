from ..chats import GroupCallParticipant
from ..update import Update


class UpdatedGroupCallParticipant(Update):
    def __init__(
        self,
        chat_id: int,
        action: GroupCallParticipant.Action,
        participant: GroupCallParticipant,
    ):
        super().__init__(chat_id)
        self.action = action
        self.participant = participant
