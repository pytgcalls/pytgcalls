import random
from typing import Any
from typing import Callable
from typing import List
from typing import Optional

from ntgcalls import Protocol
from ntgcalls import RTCServer
from ntgcalls import SsrcGroup

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

    async def join_presentation(
        self,
        chat_id: int,
        json_join: str,
    ):
        pass

    async def leave_presentation(
        self,
        chat_id: int,
    ):
        pass

    async def request_call(
        self,
        user_id: int,
        g_a_hash: bytes,
        protocol: Protocol,
    ):
        pass

    async def accept_call(
        self,
        user_id: int,
        g_b: bytes,
        protocol: Protocol,
    ):
        pass

    async def confirm_call(
        self,
        user_id: int,
        g_a: bytes,
        key_fingerprint: int,
        protocol: Protocol,
    ):
        pass

    async def send_signaling(
        self,
        user_id: int,
        data: bytes,
    ):
        pass

    async def discard_call(
        self,
        chat_id: int,
        is_missed: bool,
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
        video_paused: Optional[bool],
        video_stopped: Optional[bool],
        presentation_paused: Optional[bool],
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
    def parse_source(source) -> Optional[GroupCallParticipant.SourceInfo]:
        if not source:
            return None
        return GroupCallParticipant.SourceInfo(
            source.endpoint,
            [
                SsrcGroup(
                    source_group.semantics,
                    [ssrc for ssrc in source_group.sources],
                )
                for source_group in source.source_groups
            ],
        )

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
            BridgedClient.parse_source(participant.video),
            BridgedClient.parse_source(participant.presentation),
        )

    @staticmethod
    def chat_id(input_peer) -> int:
        class_name = input_peer.__class__.__name__
        if class_name in ['PeerUser', 'InputPeerUser']:
            return input_peer.user_id
        elif class_name in ['Channel', 'ChannelForbidden']:
            return -1000000000000 - input_peer.id
        elif hasattr(input_peer, 'channel_id'):
            return -1000000000000 - input_peer.channel_id
        elif class_name == 'Chat':
            return -input_peer.id
        else:
            return -input_peer.chat_id

    @staticmethod
    def user_from_call(call) -> Optional[int]:
        class_name = call.__class__.__name__
        if class_name in ['PhoneCallAccepted', 'PhoneCallWaiting']:
            return call.participant_id
        elif class_name in ['PhoneCallRequested', 'PhoneCall']:
            return call.admin_id
        return None

    @staticmethod
    def parse_servers(servers) -> List[RTCServer]:
        return [
            RTCServer(
                server.id,
                server.ip,
                server.ipv6,
                server.port,
                server.username,
                server.password,
                server.turn,
                server.stun,
                False,
                None,
            ) if server.__class__.__name__ == 'PhoneConnectionWebrtc' else
            RTCServer(
                server.id,
                server.ip,
                server.ipv6,
                server.port,
                None,
                None,
                True,
                False,
                server.tcp,
                server.peer_tag,
            )
            for server in servers
        ]

    @staticmethod
    def rnd_id() -> int:
        return random.randint(0, 0x7FFFFFFF - 1)

    async def get_dhc(self):
        pass

    def on_update(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self.add_handler(func)

        return decorator

    async def get_id(self):
        pass

    async def get_full_chat(self, chat_id: int):
        pass
