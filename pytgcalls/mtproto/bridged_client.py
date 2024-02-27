import random
from typing import Any
from typing import Callable
from typing import Optional

from ..handlers import HandlersHolder
from ..types import GroupCallParticipant


class BridgedClient(HandlersHolder):

    async def get_call(
        self,
        chat_id: int,
    ):
        pass

    async def join_group_call(
        self,
        chat_id: int,
        json_join: str,
        invite_hash: str,
        have_video: bool,
        join_as: Any,
    ):
        pass

    async def create_group_call(
        self,
        chat_id: int,
    ):
        pass

    async def leave_group_call(
        self,
        chat_id: int,
    ):
        pass

    async def get_group_call_participants(
        self,
        chat_id: int,
    ):
        pass

    async def change_volume(
        self,
        chat_id: int,
        volume: int,
        participant: Any,
    ):
        pass

    async def set_call_status(
        self,
        chat_id: int,
        muted_status: Optional[bool],
        paused_status: Optional[bool],
        stopped_status: Optional[bool],
        participant: Any,
    ):
        pass

    async def get_participants(
        self,
        input_call: Any,
    ):
        pass

    async def resolve_peer(
        self,
        user_id: int,
    ):
        pass

    def is_connected(self):
        pass

    def no_updates(self):
        pass

    async def start(self):
        pass

    @staticmethod
    def package_name(obj):
        return str(obj.__class__.__module__).split('.')[0]

    @staticmethod
    def parse_participant(participant):
        return GroupCallParticipant(
            BridgedClient.chat_id(participant.peer),
            bool(participant.muted),
            bool(participant.muted) != bool(participant.can_self_unmute),
            bool(participant.video) or
            bool(participant.presentation),
            bool(participant.presentation),
            bool(participant.video),
            bool(participant.raise_hand_rating),
            participant.volume // 100
            if participant.volume is not None else 100,
            bool(participant.just_joined),
            bool(participant.left),
        )

    @staticmethod
    def chat_id(input_peer) -> int:
        is_channel = hasattr(input_peer, 'channel_id')
        is_channel_update = input_peer.__class__.__name__ == 'Channel'
        is_chat = input_peer.__class__.__name__ == 'Chat'
        is_user = input_peer.__class__.__name__ == 'PeerUser' or \
            input_peer.__class__.__name__ == 'InputPeerUser'
        is_forbidden = input_peer.__class__.__name__ == 'ChannelForbidden'
        if is_user:
            return input_peer.user_id
        elif is_channel:
            return -1000000000000 - input_peer.channel_id
        elif is_channel_update or is_forbidden:
            return -1000000000000 - input_peer.id
        elif is_chat:
            return -input_peer.id
        else:
            return -input_peer.chat_id

    @staticmethod
    def rnd_id() -> int:
        return random.randint(0, 2147483647)

    def on_update(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self.add_handler(func)

        return decorator

    async def get_id(self):
        pass

    async def get_full_chat(self, chat_id: int):
        pass
