import json
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from hydrogram import Client
from hydrogram import ContinuePropagation
from hydrogram.raw.base import InputPeer
from hydrogram.raw.base import InputUser
from hydrogram.raw.functions.channels import GetFullChannel
from hydrogram.raw.functions.messages import GetDhConfig
from hydrogram.raw.functions.messages import GetFullChat
from hydrogram.raw.functions.phone import AcceptCall
from hydrogram.raw.functions.phone import ConfirmCall
from hydrogram.raw.functions.phone import CreateGroupCall
from hydrogram.raw.functions.phone import DiscardCall
from hydrogram.raw.functions.phone import EditGroupCallParticipant
from hydrogram.raw.functions.phone import GetGroupCall
from hydrogram.raw.functions.phone import GetGroupParticipants
from hydrogram.raw.functions.phone import JoinGroupCall
from hydrogram.raw.functions.phone import JoinGroupCallPresentation
from hydrogram.raw.functions.phone import LeaveGroupCall
from hydrogram.raw.functions.phone import LeaveGroupCallPresentation
from hydrogram.raw.functions.phone import RequestCall
from hydrogram.raw.functions.phone import SendSignalingData
from hydrogram.raw.types import Channel
from hydrogram.raw.types import ChannelForbidden
from hydrogram.raw.types import Chat
from hydrogram.raw.types import ChatForbidden
from hydrogram.raw.types import DataJSON
from hydrogram.raw.types import GroupCall
from hydrogram.raw.types import GroupCallDiscarded
from hydrogram.raw.types import InputChannel
from hydrogram.raw.types import InputGroupCall
from hydrogram.raw.types import InputPeerChannel
from hydrogram.raw.types import InputPhoneCall
from hydrogram.raw.types import MessageActionChatDeleteUser
from hydrogram.raw.types import MessageActionInviteToGroupCall
from hydrogram.raw.types import MessageService
from hydrogram.raw.types import PeerChat
from hydrogram.raw.types import PhoneCall
from hydrogram.raw.types import PhoneCallAccepted
from hydrogram.raw.types import PhoneCallDiscarded
from hydrogram.raw.types import PhoneCallDiscardReasonHangup
from hydrogram.raw.types import PhoneCallDiscardReasonMissed
from hydrogram.raw.types import PhoneCallProtocol
from hydrogram.raw.types import PhoneCallRequested
from hydrogram.raw.types import PhoneCallWaiting
from hydrogram.raw.types import UpdateChannel
from hydrogram.raw.types import UpdateGroupCall
from hydrogram.raw.types import UpdateGroupCallConnection
from hydrogram.raw.types import UpdateGroupCallParticipants
from hydrogram.raw.types import UpdateNewChannelMessage
from hydrogram.raw.types import UpdateNewMessage
from hydrogram.raw.types import UpdatePhoneCall
from hydrogram.raw.types import UpdatePhoneCallSignalingData
from hydrogram.raw.types import Updates
from hydrogram.raw.types.messages import DhConfig
from ntgcalls import Protocol

from ..types import CallProtocol
from ..types import ChatUpdate
from ..types import GroupCallParticipant
from ..types import RawCallUpdate
from ..types import UpdatedGroupCallParticipant
from .bridged_client import BridgedClient
from .client_cache import ClientCache


class HydrogramClient(BridgedClient):
    def __init__(
        self,
        cache_duration: int,
        client: Client,
    ):
        super().__init__()
        self._app: Client = client
        self._cache: ClientCache = ClientCache(
            cache_duration,
            self,
        )

        @self._app.on_raw_update(group=-1)
        async def on_update(_, update, __, chats):
            if isinstance(
                update,
                UpdatePhoneCallSignalingData,
            ):
                user_id = self._cache.get_user_id(update.phone_call_id)
                if user_id is not None:
                    await self.propagate(
                        RawCallUpdate(
                            user_id,
                            RawCallUpdate.Type.SIGNALING_DATA,
                            signaling_data=update.data,
                        ),
                    )

            if isinstance(
                update,
                UpdatePhoneCall,
            ):
                if isinstance(
                    update.phone_call,
                    (PhoneCallAccepted, PhoneCallRequested, PhoneCallWaiting),
                ):
                    self._cache.set_phone_call(
                        self.user_from_call(update.phone_call),
                        InputPhoneCall(
                            id=update.phone_call.id,
                            access_hash=update.phone_call.access_hash,
                        ),
                    )
                if isinstance(update.phone_call, PhoneCallAccepted):
                    await self.propagate(
                        RawCallUpdate(
                            self.user_from_call(update.phone_call),
                            RawCallUpdate.Type.ACCEPTED,
                            update.phone_call.g_b,
                            CallProtocol(
                                update.phone_call.protocol.library_versions,
                            ),
                        ),
                    )
                if isinstance(update.phone_call, PhoneCallDiscarded):
                    user_id = self._cache.get_user_id(update.phone_call.id)
                    if user_id is not None:
                        self._cache.drop_phone_call(
                            user_id,
                        )
                        await self.propagate(
                            ChatUpdate(
                                user_id,
                                ChatUpdate.Status.DISCARDED_CALL,
                            ),
                        )
                if isinstance(update.phone_call, PhoneCallRequested):
                    await self.propagate(
                        RawCallUpdate(
                            self.user_from_call(update.phone_call),
                            RawCallUpdate.Type.REQUESTED,
                            update.phone_call.g_a_hash,
                            CallProtocol(
                                update.phone_call.protocol.library_versions,
                            ),
                        ),
                    )
                if isinstance(update.phone_call, PhoneCall):
                    await self.propagate(
                        RawCallUpdate(
                            self.user_from_call(update.phone_call),
                            RawCallUpdate.Type.CONFIRMED,
                            update.phone_call.g_a_or_b,
                            CallProtocol(
                                update.phone_call.protocol.library_versions,
                                update.phone_call.p2p_allowed,
                                self.parse_servers(
                                    update.phone_call.connections,
                                ),
                            ),
                            update.phone_call.key_fingerprint,
                        ),
                    )

            if isinstance(
                update,
                UpdateGroupCallParticipants,
            ):
                participants = update.participants
                for participant in participants:
                    result = self._cache.set_participants_cache_call(
                        update.call.id,
                        self.parse_participant(participant),
                    )
                    if result is not None:
                        await self.propagate(
                            UpdatedGroupCallParticipant(
                                self._cache.get_chat_id(update.call.id),
                                result,
                            ),
                        )
            if isinstance(
                update,
                UpdateGroupCall,
            ):
                chat_id = self.chat_id(chats[update.chat_id])
                if isinstance(
                    update.call,
                    GroupCall,
                ):
                    if update.call.schedule_date is None:
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
                    self._cache.drop_cache(chat_id)
                    await self.propagate(
                        ChatUpdate(
                            chat_id,
                            ChatUpdate.Status.CLOSED_VOICE_CHAT,
                        ),
                    )
            if isinstance(
                update,
                UpdateChannel,
            ):
                chat_id = self.chat_id(update)
                if len(chats) > 0:
                    if isinstance(
                        chats[update.channel_id],
                        ChannelForbidden,
                    ):
                        self._cache.drop_cache(chat_id)
                        await self.propagate(
                            ChatUpdate(
                                chat_id,
                                ChatUpdate.Status.KICKED,
                            ),
                        )
            if isinstance(
                update,
                (UpdateNewChannelMessage, UpdateNewMessage),
            ):
                if isinstance(
                    update.message,
                    MessageService,
                ):
                    chat_id = self.chat_id(update.message.peer_id)
                    if isinstance(
                        update.message.action,
                        MessageActionInviteToGroupCall,
                    ):
                        if isinstance(
                            update.message.peer_id,
                            PeerChat,
                        ):
                            await self.propagate(
                                ChatUpdate(
                                    chat_id,
                                    ChatUpdate.Status.INVITED_VOICE_CHAT,
                                    update.message.action,
                                ),
                            )
                    if isinstance(
                        update.message.action,
                        MessageActionChatDeleteUser,
                    ):
                        if isinstance(
                            update.message.peer_id,
                            PeerChat,
                        ):
                            if isinstance(
                                chats[update.message.peer_id.chat_id],
                                ChatForbidden,
                            ):
                                self._cache.drop_cache(chat_id)
                                await self.propagate(
                                    ChatUpdate(
                                        chat_id,
                                        ChatUpdate.Status.KICKED,
                                    ),
                                )
            if isinstance(
                chats,
                Dict,
            ):
                for group_id in chats:
                    if isinstance(
                        update,
                        (UpdateNewChannelMessage, UpdateNewMessage),
                    ):
                        if isinstance(
                            update.message,
                            MessageService,
                        ):
                            if isinstance(
                                chats[group_id],
                                (Channel, Chat),
                            ):
                                chat_id = self.chat_id(chats[group_id])
                                if chats[group_id].left:
                                    self._cache.drop_cache(
                                        chat_id,
                                    )
                                    await self.propagate(
                                        ChatUpdate(
                                            chat_id,
                                            ChatUpdate.Status.LEFT_GROUP,
                                        ),
                                    )
            raise ContinuePropagation()

    async def get_call(
        self,
        chat_id: int,
    ) -> Optional[InputGroupCall]:
        chat = await self._app.resolve_peer(chat_id)
        if isinstance(chat, InputPeerChannel):
            input_call = (
                await self._app.invoke(
                    GetFullChannel(
                        channel=InputChannel(
                            channel_id=chat.channel_id,
                            access_hash=chat.access_hash,
                        ),
                    ),
                )
            ).full_chat.call
        else:
            input_call = (
                await self._app.invoke(
                    GetFullChat(chat_id=chat.chat_id),
                )
            ).full_chat.call

        if input_call is not None:
            raw_call = (
                await self._app.invoke(
                    GetGroupCall(
                        call=input_call,
                        limit=-1,
                    ),
                )
            )
            call: GroupCall = raw_call.call
            participants: List[GroupCallParticipant] = raw_call.participants
            for participant in participants:
                self._cache.set_participants_cache_chat(
                    chat_id,
                    call.id,
                    self.parse_participant(participant),
                )
            if call.schedule_date is not None:
                return None

        return input_call

    async def get_dhc(self) -> DhConfig:
        return await self._app.invoke(
            GetDhConfig(
                version=0,
                random_length=256,
            ),
        )

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
    ) -> List[GroupCallParticipant]:
        participants = []
        next_offset = ''
        while True:
            result = await self._app.invoke(
                GetGroupParticipants(
                    call=input_call,
                    ids=[],
                    sources=[],
                    offset=next_offset,
                    limit=0,
                ),
            )
            participants.extend(result.participants)
            if not (next_offset := result.next_offset):
                break
        return [
            self.parse_participant(participant)
            for participant in participants
        ]

    async def join_group_call(
        self,
        chat_id: int,
        json_join: str,
        invite_hash: str,
        have_video: bool,
        join_as: InputPeer,
    ) -> str:
        chat_call = await self._cache.get_full_chat(chat_id)
        if chat_call is not None:
            result: Updates = await self._app.invoke(
                JoinGroupCall(
                    call=chat_call,
                    params=DataJSON(data=json_join),
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
                        self._cache.set_participants_cache_call(
                            update.call.id,
                            self.parse_participant(participant),
                        )
                if isinstance(update, UpdateGroupCallConnection):
                    return update.params.data

        return json.dumps({'transport': None})

    async def join_presentation(
        self,
        chat_id: int,
        json_join: str,
    ):
        chat_call = await self._cache.get_full_chat(chat_id)
        if chat_call is not None:
            result: Updates = await self._app.invoke(
                JoinGroupCallPresentation(
                    call=chat_call,
                    params=DataJSON(data=json_join),
                ),
            )
            for update in result.updates:
                if isinstance(update, UpdateGroupCallConnection):
                    return update.params.data

        return json.dumps({'transport': None})

    async def leave_presentation(
        self,
        chat_id: int,
    ):
        chat_call = await self._cache.get_full_chat(chat_id)
        if chat_call is not None:
            await self._app.invoke(
                LeaveGroupCallPresentation(
                    call=chat_call,
                ),
            )

    async def request_call(
        self,
        user_id: int,
        g_a_hash: bytes,
        protocol: Protocol,
    ):
        await self._app.invoke(
            RequestCall(
                user_id=await self.resolve_peer(user_id),
                random_id=self.rnd_id(),
                g_a_hash=g_a_hash,
                protocol=self.parse_protocol(protocol),
                video=False,
            ),
        )

    async def accept_call(
        self,
        user_id: int,
        g_b: bytes,
        protocol: Protocol,
    ):
        await self._app.invoke(
            AcceptCall(
                peer=self._cache.get_phone_call(user_id),
                g_b=g_b,
                protocol=self.parse_protocol(protocol),
            ),
        )

    async def confirm_call(
        self,
        user_id: int,
        g_a: bytes,
        key_fingerprint: int,
        protocol: Protocol,
    ) -> CallProtocol:
        res = (
            await self._app.invoke(
                ConfirmCall(
                    peer=self._cache.get_phone_call(user_id),
                    g_a=g_a,
                    key_fingerprint=key_fingerprint,
                    protocol=self.parse_protocol(protocol),
                ),
            )
        ).phone_call
        return CallProtocol(
            res.protocol.library_versions,
            res.p2p_allowed,
            self.parse_servers(res.connections),
        )

    async def send_signaling(
        self,
        user_id: int,
        data: bytes,
    ):
        await self._app.invoke(
            SendSignalingData(
                peer=self._cache.get_phone_call(user_id),
                data=data,
            ),
        )

    async def create_group_call(
        self,
        chat_id: int,
    ):
        result: Updates = await self._app.invoke(
            CreateGroupCall(
                peer=await self.resolve_peer(chat_id),
                random_id=self.rnd_id(),
            ),
        )
        for update in result.updates:
            if isinstance(
                    update,
                    UpdateGroupCall,
            ):
                if isinstance(
                        update.call,
                        GroupCall,
                ):
                    if update.call.schedule_date is None:
                        self._cache.set_cache(
                            chat_id,
                            InputGroupCall(
                                access_hash=update.call.access_hash,
                                id=update.call.id,
                            ),
                        )

    async def leave_group_call(
        self,
        chat_id: int,
    ):
        chat_call = await self._cache.get_full_chat(chat_id)
        if chat_call is not None:
            await self._app.invoke(
                LeaveGroupCall(
                    call=chat_call,
                    source=0,
                ),
            )

    async def discard_call(
        self,
        chat_id: int,
        is_missed: bool,
    ):
        peer = self._cache.get_phone_call(chat_id)
        if peer is None:
            return
        reason = (
            PhoneCallDiscardReasonMissed()
            if is_missed
            else PhoneCallDiscardReasonHangup()
        )
        await self._app.invoke(
            DiscardCall(
                peer=peer,
                duration=0,
                reason=reason,
                connection_id=0,
                video=False,
            ),
        )
        self._cache.drop_phone_call(chat_id)

    async def change_volume(
        self,
        chat_id: int,
        volume: int,
        participant: InputPeer,
    ):
        chat_call = await self._cache.get_full_chat(chat_id)
        if chat_call is not None:
            await self._app.invoke(
                EditGroupCallParticipant(
                    call=chat_call,
                    participant=participant,
                    muted=False,
                    volume=volume * 100,
                ),
            )

    async def set_call_status(
        self,
        chat_id: int,
        muted_status: Optional[bool],
        video_paused: Optional[bool],
        video_stopped: Optional[bool],
        presentation_paused: Optional[bool],
        participant: InputPeer,
    ):
        chat_call = await self._cache.get_full_chat(chat_id)
        if chat_call is not None:
            await self._app.invoke(
                EditGroupCallParticipant(
                    call=chat_call,
                    participant=participant,
                    muted=muted_status,
                    video_paused=video_paused,
                    video_stopped=video_stopped,
                    presentation_paused=presentation_paused,
                ),
            )

    async def get_full_chat(self, chat_id: int):
        return await self._cache.get_full_chat(chat_id)

    async def resolve_peer(
            self,
            user_id: Union[int, str],
    ) -> Union[InputPeer, InputUser, InputChannel]:
        return await self._app.resolve_peer(user_id)

    @staticmethod
    def parse_protocol(protocol: Protocol) -> PhoneCallProtocol:
        return PhoneCallProtocol(
            min_layer=protocol.min_layer,
            max_layer=protocol.max_layer,
            udp_p2p=protocol.udp_p2p,
            udp_reflector=protocol.udp_reflector,
            library_versions=protocol.library_versions,
        )

    async def get_id(self) -> int:
        return (await self._app.get_me()).id

    def is_connected(self) -> bool:
        return self._app.is_connected

    def no_updates(self):
        return self._app.no_updates

    async def start(self):
        await self._app.start()
