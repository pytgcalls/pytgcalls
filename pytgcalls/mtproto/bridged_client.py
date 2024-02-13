import asyncio
import random
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from ..types import GroupCallParticipant


class BridgedClient:
    HANDLERS_LIST: Dict[str, List[Callable]] = {
        'CLOSED_HANDLER': [],
        'KICK_HANDLER': [],
        'INVITE_HANDLER': [],
        'LEFT_HANDLER': [],
        'PARTICIPANTS_HANDLER': [],
    }

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

    async def _propagate(self, event_name: str, *args, **kwargs):
        for event in self.HANDLERS_LIST[event_name]:
            asyncio.ensure_future(event(*args, **kwargs))

    def on_closed_voice_chat(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self.HANDLERS_LIST['CLOSED_HANDLER'].append(func)
            return func

        return decorator

    def on_kicked(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self.HANDLERS_LIST['KICK_HANDLER'].append(func)
            return func

        return decorator

    def on_receive_invite(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self.HANDLERS_LIST['INVITE_HANDLER'].append(func)
            return func

        return decorator

    async def get_id(self):
        pass

    def on_left_group(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self.HANDLERS_LIST['LEFT_HANDLER'].append(func)
            return func

        return decorator

    def on_participants_change(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self.HANDLERS_LIST['PARTICIPANTS_HANDLER'].append(func)
            return func

        return decorator

    async def get_full_chat(self, chat_id: int):
        pass
