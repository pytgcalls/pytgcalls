from typing import Any
from typing import Callable
from typing import List
from typing import Optional

from ntgcalls import Protocol

from ..exceptions import InvalidMTProtoClient
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
        elif self.package_name == 'hydrogram':
            from .hydrogram_client import HydrogramClient
            self._bind_client = HydrogramClient(
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

    async def join_group_call(
        self,
        chat_id: int,
        json_join: str,
        invite_hash: str,
        have_video: bool,
        join_as: Any,
    ) -> str:
        if self._bind_client is not None:
            return await self._bind_client.join_group_call(
                chat_id,
                json_join,
                invite_hash,
                have_video,
                join_as,
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
    ):
        if self._bind_client is not None:
            return await self._bind_client.request_call(
                user_id,
                g_a_hash,
                protocol,
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

    async def get_full_chat(
        self,
        chat_id: int,
    ):
        if self._bind_client is not None:
            return await self._bind_client.get_full_chat(
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

    def on_update(self) -> Callable:
        if self._bind_client is not None:
            return self._bind_client.on_update()
        raise InvalidMTProtoClient()
