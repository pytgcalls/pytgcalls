from typing import List, Dict, Optional

from pytgcalls.types.groups import GroupCallParticipant


class ParticipantList:
    def __init__(self):
        self._list_participants: Dict[int, GroupCallParticipant] = {}
        self.last_mtproto_update = 0

    def set_participant(
        self,
        user_id: int,
        muted: bool,
        muted_by_admin: bool,
        have_video: bool,
        raised_hand: bool,
        volume: int,
    ):
        participant = GroupCallParticipant(
            user_id,
            muted,
            muted_by_admin,
            have_video,
            raised_hand,
            volume,
        )
        self._list_participants[user_id] = participant
        return participant

    def remove_participant(
        self,
        user_id: int,
        muted,
        muted_by_admin,
        have_video,
        raised_hand,
        volume,
    ):
        participant = GroupCallParticipant(
            user_id,
            muted,
            muted_by_admin,
            have_video,
            raised_hand,
            volume,
        )
        if user_id in self._list_participants:
            del self._list_participants[user_id]
        return participant

    def get_participants(
        self,
    ):
        return [
            self._list_participants[user_id]
            for user_id in self._list_participants
        ]
