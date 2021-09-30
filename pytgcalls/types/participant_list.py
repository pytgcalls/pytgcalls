from typing import Dict

from pytgcalls.types.groups import GroupCallParticipant
from pytgcalls.types.list import List


class ParticipantList:
    def __init__(
        self,
        input_id: int,
    ):
        self._list_participants: Dict[int, GroupCallParticipant] = {}
        self.last_mtproto_update: int = 0
        self.input_id: int = input_id

    def set_participant(
        self,
        user_id: int,
        muted: bool,
        muted_by_admin: bool,
        video: bool,
        screen_sharing: bool,
        video_camera: bool,
        raised_hand: bool,
        volume: int,
    ):
        participant = GroupCallParticipant(
            user_id,
            muted,
            muted_by_admin,
            video,
            screen_sharing,
            video_camera,
            raised_hand,
            volume,
        )
        self._list_participants[user_id] = participant
        return participant

    def remove_participant(
        self,
        user_id: int,
        muted: bool,
        muted_by_admin: bool,
        video: bool,
        screen_sharing: bool,
        video_camera: bool,
        raised_hand: bool,
        volume: int,
    ):
        participant = GroupCallParticipant(
            user_id,
            muted,
            muted_by_admin,
            video,
            screen_sharing,
            video_camera,
            raised_hand,
            volume,
        )
        if user_id in self._list_participants:
            del self._list_participants[user_id]
        return participant

    def get_participants(
        self,
    ):
        return List([
            self._list_participants[user_id]
            for user_id in self._list_participants
        ])
