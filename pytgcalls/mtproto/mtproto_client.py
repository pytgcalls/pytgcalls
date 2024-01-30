from typing import Any
from typing import Callable
from typing import List
from typing import Optional

from ..exceptions import InvalidMTProtoClient
from ..types.groups import GroupCallParticipant
from .bridged_client import BridgedClient


class MtProtoClient:
    def __init__(
        self,
        cache_duration: int,
        client: Any,
    ):
        self._bind_client: Optional[BridgedClient] = None
        if client.__class__.__module__ == 'pyrogram.client':
            from .pyrogram_client import PyrogramClient
            self._bind_client = PyrogramClient(
                cache_duration,
                client,
            )
        elif client.__class__.__module__ == 'telethon.client.telegramclient':
            from .telethon_client import TelethonClient
            self._bind_client = TelethonClient(
                cache_duration,
                client,
            )
        elif client.__class__.__module__ == 'hydrogram.client':
            from .hydrogram_client import HydrogramClient
            self._bind_client = HydrogramClient(
                cache_duration,
                client,
            )
        else:
            raise InvalidMTProtoClient()

    @property
    def client(self):
        client_name = self._bind_client.__class__.__name__
        if client_name == 'PyrogramClient':
            return 'pyrogram'
        elif client_name == 'TelethonClient':
            return 'telethon'
        elif client_name == 'HydrogramClient':
            return 'hydrogram'
        else:
            return 'unknown'

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
        paused_status: Optional[bool],
        stopped_status: Optional[bool],
        participant: Any,
    ):
        if self._bind_client is not None:
            await self._bind_client.set_call_status(
                chat_id,
                muted_status,
                paused_status,
                stopped_status,
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

    async def start(self):
        if self._bind_client is not None:
            await self._bind_client.start()
        else:
            raise InvalidMTProtoClient()

    def on_closed_voice_chat(self) -> Callable:
        if self._bind_client is not None:
            return self._bind_client.on_closed_voice_chat()
        raise InvalidMTProtoClient()

    def on_kicked(self) -> Callable:
        if self._bind_client is not None:
            return self._bind_client.on_kicked()
        raise InvalidMTProtoClient()

    def on_receive_invite(self) -> Callable:
        if self._bind_client is not None:
            return self._bind_client.on_receive_invite()
        raise InvalidMTProtoClient()

    def on_left_group(self) -> Callable:
        if self._bind_client is not None:
            return self._bind_client.on_left_group()
        raise InvalidMTProtoClient()

    def on_participants_change(self) -> Callable:
        if self._bind_client is not None:
            return self._bind_client.on_participants_change()
        raise InvalidMTProtoClient()
