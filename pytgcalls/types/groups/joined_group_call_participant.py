from ...types.groups import GroupCallParticipant
from ...types.update import Update


class JoinedGroupCallParticipant(Update):
    def __init__(
        self,
        chat_id: int,
        participant: GroupCallParticipant,
    ):
        super().__init__(chat_id)
        self.participant = participant
