from ...types.groups.group_call_participant import GroupCallParticipant
from ...types.update import Update


class JoinedGroupCallParticipant(Update):
    """A participant joined to the Group Call

    Attributes:
        chat_id (``int``):
            Unique identifier of chat.
        participant (:obj:`~pytgcalls.types.GroupCallParticipant()`):
            Info about a group call participant

    Parameters:
        chat_id (``int``):
            Unique identifier of chat.
        participant (:obj:`~pytgcalls.types.GroupCallParticipant()`):
            Info about a group call participant
    """

    def __init__(
        self,
        chat_id: int,
        participant: GroupCallParticipant,
    ):
        super().__init__(chat_id)
        self.participant = participant
