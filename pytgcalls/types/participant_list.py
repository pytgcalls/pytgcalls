from typing import Dict

from ..types.chats import GroupCallParticipant
from ..types.list import List


class ParticipantList:
    def __init__(
        self,
        input_id: int,
    ):
        self._list_participants: Dict[int, GroupCallParticipant] = {}
        self.last_mtproto_update: int = 0
        self.input_id: int = input_id

    def update_participant(
        self,
        participant: GroupCallParticipant,
    ):
        if participant.action == GroupCallParticipant.Action.LEFT:
            if participant.user_id in self._list_participants:
                del self._list_participants[participant.user_id]
        else:
            self._list_participants[participant.user_id] = participant
        return participant

    def get_participants(
        self,
    ):
        return List([
            self._list_participants[user_id]
            for user_id in self._list_participants
        ])
