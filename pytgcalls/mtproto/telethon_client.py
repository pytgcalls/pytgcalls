import json
from typing import Callable
from typing import Dict
from typing import Optional

from telethon import TelegramClient
from telethon.errors import ChannelPrivateError
from telethon.events import Raw
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.phone import EditGroupCallParticipantRequest
from telethon.tl.functions.phone import GetGroupParticipantsRequest
from telethon.tl.functions.phone import JoinGroupCallRequest
from telethon.tl.functions.phone import LeaveGroupCallRequest
from telethon.tl.types import ChatForbidden
from telethon.tl.types import DataJSON
from telethon.tl.types import GroupCall
from telethon.tl.types import GroupCallDiscarded
from telethon.tl.types import InputChannel
from telethon.tl.types import InputGroupCall
from telethon.tl.types import InputPeerChannel
from telethon.tl.types import MessageActionChatDeleteUser
from telethon.tl.types import MessageActionInviteToGroupCall
from telethon.tl.types import MessageService
from telethon.tl.types import PeerChat
from telethon.tl.types import TypeInputPeer
from telethon.tl.types import UpdateChannel
from telethon.tl.types import UpdateGroupCall
from telethon.tl.types import UpdateGroupCallConnection
from telethon.tl.types import UpdateGroupCallParticipants
from telethon.tl.types import UpdateNewChannelMessage
from telethon.tl.types import UpdateNewMessage
from telethon.tl.types import Updates

from .bridged_client import BridgedClient
from .client_cache import ClientCache


class TelethonClient(BridgedClient):
    def __init__(
        self,
        cache_duration: int,
        client: TelegramClient,
    ):
        self._app: TelegramClient = client
        self._handler: Dict[str, Callable] = {}
        self._cache: ClientCache = ClientCache(
            cache_duration,
            self,
        )

        @self._app.on(Raw())
        async def on_update(update):
            if isinstance(
                update,
                UpdateGroupCallParticipants,
            ):
                participants = update.participants
                for participant in participants:
                    result = self._cache.set_participants_cache(
                        update.call.id,
                        self.chat_id(participant.peer),
                        participant.muted,
                        participant.volume,
                        participant.can_self_unmute,
                        participant.video is not None or
                        participant.presentation is not None,
                        participant.presentation is not None,
                        participant.video is not None,
                        participant.raise_hand_rating,
                        participant.left,
                    )
                    if result is not None:
                        if 'PARTICIPANTS_HANDLER' in self._handler:
                            await self._handler['PARTICIPANTS_HANDLER'](
                                self._cache.get_chat_id(update.call.id),
                                result,
                                participant.just_joined,
                                participant.left,
                            )
            if isinstance(
                update,
                UpdateGroupCall,
            ):
                chat_id = self.chat_id(
                    await self._app.get_entity(update.chat_id),
                )
                if isinstance(
                    update.call,
                    GroupCall,
                ):
                    self._cache.set_cache(
                        chat_id,
                        InputGroupCall(
                            access_hash=update.call.access_hash,
                            id=update.call.id,
                        ),
                    )
                if isinstance(
                    update.call,
                    GroupCallDiscarded,
                ):
                    self._cache.drop_cache(
                        chat_id,
                    )
                    if 'CLOSED_HANDLER' in self._handler:
                        await self._handler['CLOSED_HANDLER'](
                            chat_id,
                        )
            if isinstance(
                update,
                UpdateChannel,
            ):
                chat_id = self.chat_id(update)
                try:
                    await self._app.get_entity(chat_id)
                except ChannelPrivateError:
                    self._cache.drop_cache(chat_id)
                    if 'KICK_HANDLER' in self._handler:
                        await self._handler['KICK_HANDLER'](
                            chat_id,
                        )

            if isinstance(
                update,
                UpdateNewChannelMessage,
            ) or isinstance(
                update,
                UpdateNewMessage,
            ):
                if isinstance(
                    update.message,
                    MessageService,
                ):
                    if isinstance(
                        update.message.action,
                        MessageActionInviteToGroupCall,
                    ):
                        if 'INVITE_HANDLER' in self._handler:
                            await self._handler['INVITE_HANDLER'](
                                update.message.action,
                            )
                    if isinstance(update.message.out, bool):
                        if update.message.out:
                            self._cache.drop_cache(update.message.action)
                            chat_id = self.chat_id(update.message.peer_id)
                            if 'LEFT_HANDLER' in self._handler:
                                await self._handler['LEFT_HANDLER'](
                                    chat_id,
                                )
                    if isinstance(
                        update.message.action,
                        MessageActionChatDeleteUser,
                    ):
                        if isinstance(
                            update.message.peer_id,
                            PeerChat,
                        ):
                            chat_id = self.chat_id(update.message.peer_id)
                            if isinstance(
                                await self._app.get_entity(chat_id),
                                ChatForbidden,
                            ):
                                self._cache.drop_cache(chat_id)
                                if 'KICK_HANDLER' in self._handler:
                                    await self._handler['KICK_HANDLER'](
                                        chat_id,
                                    )

    async def get_call(
        self,
        chat_id: int,
    ) -> Optional[InputGroupCall]:
        chat = await self._app.get_input_entity(chat_id)
        if isinstance(chat, InputPeerChannel):
            return (
                await self._app(
                    GetFullChannelRequest(
                        InputChannel(
                            chat.channel_id,
                            chat.access_hash,
                        ),
                    ),
                )
            ).full_chat.call
        else:
            return (
                await self._app(
                    GetFullChatRequest(chat_id),
                )
            ).full_chat.call

    async def get_group_call_participants(
        self,
        chat_id: int,
    ):
        return await self._cache.get_participant_list(
            chat_id,
        )

    async def get_participants(
        self,
        input_call: InputGroupCall,
    ):
        return [
            {
                'user_id': self.chat_id(participant.peer),
                'muted': participant.muted,
                'volume': participant.volume,
                'can_self_unmute': participant.can_self_unmute,
                'video': participant.video,
                'presentation': participant.presentation,
                'raise_hand_rating': participant.raise_hand_rating,
                'left': participant.left,
            } for participant in (
                await self._app(
                    GetGroupParticipantsRequest(
                        call=input_call,
                        ids=[],
                        sources=[],
                        offset='',
                        limit=500,
                    ),
                )
            ).participants
        ]

    async def join_group_call(
        self,
        chat_id: int,
        json_join: dict,
        invite_hash: str,
        have_video: bool,
        join_as: TypeInputPeer,
    ) -> dict:
        chat_call = await self._cache.get_full_chat(chat_id)
        if chat_call is not None:
            result: Updates = await self._app(
                JoinGroupCallRequest(
                    call=chat_call,
                    params=DataJSON(data=json.dumps(json_join)),
                    muted=False,
                    join_as=join_as,
                    video_stopped=have_video,
                    invite_hash=invite_hash,
                ),
            )
            for update in result.updates:
                if isinstance(
                    update,
                    UpdateGroupCallParticipants,
                ):
                    participants = update.participants
                    for participant in participants:
                        self._cache.set_participants_cache(
                            update.call.id,
                            self.chat_id(participant.peer),
                            participant.muted,
                            participant.volume,
                            participant.can_self_unmute,
                            participant.video is not None or
                            participant.presentation is not None,
                            participant.presentation is not None,
                            participant.video is not None,
                            participant.raise_hand_rating,
                            participant.left,
                        )
                if isinstance(update, UpdateGroupCallConnection):
                    transport = json.loads(update.params.data)[
                        'transport'
                    ]
                    return {
                        'transport': {
                            'ufrag': transport['ufrag'],
                            'pwd': transport['pwd'],
                            'fingerprints': transport['fingerprints'],
                            'candidates': transport['candidates'],
                        },
                    }
        return {'transport': None}

    def on_closed_voice_chat(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._handler['CLOSED_HANDLER'] = func
            return func
        return decorator

    def on_kicked(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._handler['KICK_HANDLER'] = func
            return func
        return decorator

    def on_receive_invite(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._handler['INVITE_HANDLER'] = func
            return func
        return decorator

    def on_left_group(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._handler['LEFT_HANDLER'] = func
            return func
        return decorator

    def on_participants_change(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._handler['PARTICIPANTS_HANDLER'] = func
            return func
        return decorator

    async def leave_group_call(
        self,
        chat_id: int,
    ):
        chat_call = await self._cache.get_full_chat(chat_id)
        if chat_call is not None:
            await self._app(
                LeaveGroupCallRequest(
                    call=chat_call,
                    source=0,
                ),
            )

    async def change_volume(
        self,
        chat_id: int,
        volume: int,
        participant: TypeInputPeer,
    ):
        chat_call = await self._cache.get_full_chat(chat_id)
        if chat_call is not None:
            await self._app(
                EditGroupCallParticipantRequest(
                    call=chat_call,
                    participant=participant,
                    muted=False,
                    volume=volume * 100,
                ),
            )

    async def set_video_call_status(
        self,
        chat_id: int,
        stopped_status: Optional[bool],
        paused_status: Optional[bool],
        participant: TypeInputPeer,
    ):
        chat_call = await self._cache.get_full_chat(chat_id)
        if chat_call is not None:
            await self._app(
                EditGroupCallParticipantRequest(
                    call=chat_call,
                    participant=participant,
                    muted=False,
                    video_stopped=stopped_status,
                    video_paused=paused_status,
                ),
            )

    async def get_full_chat(self, chat_id: int):
        return await self._cache.get_full_chat(chat_id)

    async def resolve_peer(
        self,
        user_id: int,
    ) -> TypeInputPeer:
        return await self._app.get_input_entity(user_id)

    async def get_id(self) -> int:
        return (await self._app.get_me()).id

    def is_connected(self) -> bool:
        return self._app.is_connected()

    async def start(self):
        await self._app.start()
