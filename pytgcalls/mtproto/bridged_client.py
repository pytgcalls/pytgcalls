import random
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional


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

    async def start(self):
        pass

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

    def on_closed_voice_chat(self):
        pass

    def on_kicked(self):
        pass

    def on_receive_invite(self):
        pass

    async def get_id(self):
        pass

    def on_left_group(self):
        pass

    def on_participants_change(self):
        pass

    async def get_full_chat(self, chat_id: int):
        pass
