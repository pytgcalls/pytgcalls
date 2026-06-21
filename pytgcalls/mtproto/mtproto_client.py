from typing import Any
from typing import Callable
from typing import List
from typing import Optional

from ntgcalls import MediaSegmentQuality
from ntgcalls import Protocol
from ntgcalls import SubchainRequest

from ..exceptions import InvalidMTProtoClient
from ..types.calls import ChainBlocks
from ..types.chats import GroupCallParticipant
from .bridged_client import BridgedClient


class MtProtoClient:
    def __init__(
        self,
        cache_duration: int,
        client: Any,
    ):
        self._bind_client: Optional[BridgedClient] = None
        self.package_name = BridgedClient.package_name(client)
        if self.package_name == 'pyrogram':
            from .pyrogram_client import PyrogramClient
            self._bind_client = PyrogramClient(
                cache_duration,
                client,
            )
        elif self.package_name == 'telethon':
            from .telethon_client import TelethonClient
            self._bind_client = TelethonClient(
                cache_duration,
                client,
            )
        else:
            raise InvalidMTProtoClient()

    async def get_group_call_participants(
        self,
        chat_id: int,
    ) -> Optional[List[GroupCallParticipant]]:
        if self._bind_client is not None:
            return await self._bind_client.get_group_call_participants(
                chat_id,
            )
        else:
            raise InvalidMTProtoClient()

    async def send_conference_call_broadcast(
        self,
        chat_id: int,
        block: bytes,
    ):
        if self._bind_client is not None:
            await self._bind_client.send_conference_call_broadcast(
                chat_id,
                block,
            )
        else:
            raise InvalidMTProtoClient()

    async def get_subchain_blocks(
        self,
        chat_id: int,
        subchain_request: SubchainRequest,
    ) -> Optional[ChainBlocks]:
        if self._bind_client is not None:
            return await self._bind_client.get_subchain_blocks(
                chat_id,
                subchain_request,
            )
        else:
            raise InvalidMTProtoClient()

    async def get_conference_last_block(
        self,
        chat_id: int,
    ) -> Optional[bytes]:
        if self._bind_client is not None:
            return await self._bind_client.get_conference_last_block(
                chat_id,
            )
        else:
            raise InvalidMTProtoClient()

    async def join_group_call(
        self,
        chat_id: int,
        json_join: str,
        video_stopped: bool,
        join_as: Any,
        invite_hash: Optional[str] = None,
        block: Optional[bytes] = None,
        public_key: Optional[int] = None,
    ) -> str:
        if self._bind_client is not None:
            return await self._bind_client.join_group_call(
                chat_id,
                json_join,
                video_stopped,
                join_as,
                invite_hash,
                block,
                public_key,
            )
        else:
            raise InvalidMTProtoClient()

    async def create_conference_call(
        self,
        chat_id: int,
        json_join: str,
        video_stopped: bool,
        block: bytes,
        public_key: int,
    ) -> str:
        if self._bind_client is not None:
            return await self._bind_client.create_conference_call(
                chat_id,
                json_join,
                video_stopped,
                block,
                public_key,
            )
        else:
            raise InvalidMTProtoClient()

    async def join_presentation(
        self,
        chat_id: int,
        json_join: str,
    ):
        if self._bind_client is not None:
            return await self._bind_client.join_presentation(
                chat_id,
                json_join,
            )
        else:
            raise InvalidMTProtoClient()

    async def leave_presentation(
        self,
        chat_id: int,
    ):
        if self._bind_client is not None:
            return await self._bind_client.leave_presentation(
                chat_id,
            )
        else:
            raise InvalidMTProtoClient()

    async def request_call(
        self,
        user_id: int,
        g_a_hash: bytes,
        protocol: Protocol,
        has_video: bool,
    ):
        if self._bind_client is not None:
            return await self._bind_client.request_call(
                user_id,
                g_a_hash,
                protocol,
                has_video,
            )
        else:
            raise InvalidMTProtoClient()

    async def accept_call(
        self,
        user_id: int,
        g_b: bytes,
        protocol: Protocol,
    ):
        if self._bind_client is not None:
            return await self._bind_client.accept_call(
                user_id,
                g_b,
                protocol,
            )
        else:
            raise InvalidMTProtoClient()

    async def discard_call(
        self,
        user_id: int,
        is_missed: bool,
    ):
        if self._bind_client is not None:
            return await self._bind_client.discard_call(
                user_id,
                is_missed,
            )
        else:
            raise InvalidMTProtoClient()

    async def confirm_call(
        self,
        user_id: int,
        g_a: bytes,
        key_fingerprint: int,
        protocol: Protocol,
    ):
        if self._bind_client is not None:
            return await self._bind_client.confirm_call(
                user_id,
                g_a,
                key_fingerprint,
                protocol,
            )
        else:
            raise InvalidMTProtoClient()

    async def send_signaling(
        self,
        user_id: int,
        data: bytes,
    ):
        if self._bind_client is not None:
            await self._bind_client.send_signaling(
                user_id,
                data,
            )
        else:
            raise InvalidMTProtoClient()

    async def get_dhc(self):
        if self._bind_client is not None:
            return await self._bind_client.get_dhc()
        else:
            raise InvalidMTProtoClient()

    async def create_group_call(
        self,
        chat_id: int,
    ):
        if self._bind_client is not None:
            await self._bind_client.create_group_call(
                chat_id,
            )
        else:
            raise InvalidMTProtoClient()

    async def leave_group_call(
        self,
        chat_id: int,
    ):
        if self._bind_client is not None:
            await self._bind_client.leave_group_call(
                chat_id,
            )
        else:
            raise InvalidMTProtoClient()

    async def close_voice_chat(
        self,
        chat_id: int,
    ):
        if self._bind_client is not None:
            await self._bind_client.close_voice_chat(
                chat_id,
            )
        else:
            raise InvalidMTProtoClient()

    async def change_volume(
        self,
        chat_id: int,
        volume: int,
        participant: Any,
    ):
        if self._bind_client is not None:
            await self._bind_client.change_volume(
                chat_id,
                volume,
                participant,
            )
        else:
            raise InvalidMTProtoClient()

    async def download_stream(
        self,
        chat_id: int,
        timestamp: int,
        limit: int,
        video_channel: Optional[int],
        video_quality: MediaSegmentQuality,
    ):
        if self._bind_client is not None:
            return await self._bind_client.download_stream(
                chat_id,
                timestamp,
                limit,
                video_channel,
                video_quality,
            )
        else:
            raise InvalidMTProtoClient()

    async def get_stream_timestamp(
        self,
        chat_id: int,
    ):
        if self._bind_client is not None:
            return await self._bind_client.get_stream_timestamp(
                chat_id,
            )
        else:
            raise InvalidMTProtoClient()

    async def set_call_status(
        self,
        chat_id: int,
        muted_status: Optional[bool],
        video_paused: Optional[bool],
        video_stopped: Optional[bool],
        presentation_paused: Optional[bool],
        participant: Any,
    ):
        if self._bind_client is not None:
            await self._bind_client.set_call_status(
                chat_id,
                muted_status,
                video_paused,
                video_stopped,
                presentation_paused,
                participant,
            )
        else:
            raise InvalidMTProtoClient()

    async def get_input_call(
        self,
        chat_id: int,
    ):
        if self._bind_client is not None:
            return await self._bind_client.get_input_call(
                chat_id,
            )
        raise InvalidMTProtoClient()

    async def resolve_peer(
        self,
        user_id: int,
    ):
        if self._bind_client is not None:
            return await self._bind_client.resolve_peer(
                user_id,
            )
        raise InvalidMTProtoClient()

    async def get_id(self) -> int:
        if self._bind_client is not None:
            return await self._bind_client.get_id()
        raise InvalidMTProtoClient()

    @property
    def is_connected(self) -> bool:
        if self._bind_client is not None:
            return self._bind_client.is_connected()
        raise InvalidMTProtoClient()

    @property
    def no_updates(self) -> bool:
        if self._bind_client is not None:
            return self._bind_client.no_updates()
        raise InvalidMTProtoClient()

    @property
    def mtproto_client(self):
        if self._bind_client is not None:
            return self._bind_client
        raise InvalidMTProtoClient()

    async def start(self):
        if self._bind_client is not None:
            await self._bind_client.start()
        else:
            raise InvalidMTProtoClient()

    def add_handler(self, func: Callable):
        if self._bind_client is not None:
            return self._bind_client.add_handler(func)
        raise InvalidMTProtoClient()
