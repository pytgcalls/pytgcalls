import json
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pyrogram
from ntgcalls import Protocol
from ...exceptions import UnMuteNeeded
from pyrogram import Client
from pyrogram import ContinuePropagation
from pyrogram.raw.base import InputPeer
from pyrogram.raw.base import InputUser
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetDhConfig
from pyrogram.raw.functions.messages import GetFullChat
from pyrogram.raw.functions.phone import AcceptCall
from pyrogram.raw.functions.phone import ConfirmCall
from pyrogram.raw.functions.phone import CreateGroupCall
from pyrogram.raw.functions.phone import DiscardCall
from pyrogram.raw.functions.phone import EditGroupCallParticipant
from pyrogram.raw.functions.phone import GetGroupCall
from pyrogram.raw.functions.phone import GetGroupParticipants
from pyrogram.raw.functions.phone import JoinGroupCall
from pyrogram.raw.functions.phone import JoinGroupCallPresentation
from pyrogram.raw.functions.phone import LeaveGroupCall
from pyrogram.raw.functions.phone import LeaveGroupCallPresentation
from pyrogram.raw.functions.phone import RequestCall
from pyrogram.raw.functions.phone import SendSignalingData
from pyrogram.raw.functions.phone import ToggleGroupCallSettings
from pyrogram.raw.types import Channel
from pyrogram.raw.types import ChannelForbidden
from pyrogram.raw.types import Chat
from pyrogram.raw.types import ChatForbidden
from pyrogram.raw.types import DataJSON
from pyrogram.raw.types import GroupCall
from pyrogram.raw.types import GroupCallDiscarded
from pyrogram.raw.types import InputChannel
from pyrogram.raw.types import InputGroupCall
from pyrogram.raw.types import InputPeerChannel
from pyrogram.raw.types import InputPhoneCall
from pyrogram.raw.types import MessageActionChatDeleteUser
from pyrogram.raw.types import MessageActionInviteToGroupCall
from pyrogram.raw.types import MessageService
from pyrogram.raw.types import PeerChat
from pyrogram.raw.types import PhoneCall
from pyrogram.raw.types import PhoneCallAccepted
from pyrogram.raw.types import PhoneCallDiscarded
from pyrogram.raw.types import PhoneCallDiscardReasonHangup
from pyrogram.raw.types import PhoneCallDiscardReasonMissed
from pyrogram.raw.types import PhoneCallProtocol
from pyrogram.raw.types import PhoneCallRequested
from pyrogram.raw.types import PhoneCallWaiting
from pyrogram.raw.types import UpdateChannel
from pyrogram.raw.types import UpdateGroupCall
from pyrogram.raw.types import UpdateGroupCallConnection
from pyrogram.raw.types import UpdateGroupCallParticipants
from pyrogram.raw.types import UpdateNewChannelMessage
from pyrogram.raw.types import UpdateNewMessage
from pyrogram.raw.types import UpdatePhoneCall
from pyrogram.raw.types import UpdatePhoneCallSignalingData
from pyrogram.raw.types import Updates
from pyrogram.raw.types.messages import DhConfig

from ..types import CallProtocol
from ..types import ChatUpdate
from ..types import GroupCallParticipant
from ..types import RawCallUpdate
from ..types import UpdatedGroupCallParticipant
from ..version_manager import VersionManager
from .bridged_client import BridgedClient
from .client_cache import ClientCache


class PyrogramClient(BridgedClient):
    def __init__(
        self,
        cache_duration: int,
        client: Client,
    ):
        super().__init__()
        self._app: Client = client
        if VersionManager.version_tuple(
                pyrogram.__version__,
        ) > VersionManager.version_tuple(
            '2.0.0',
        ):
            self._app.send = self._app.invoke
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
                await self._app.send(
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
                await self._app.send(
                    GetFullChat(chat_id=chat.chat_id),
                )
            ).full_chat.call

        if input_call is not None:
            raw_call = (
                await self._app.send(
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
        return await self._app.send(
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
            result = await self._app.send(
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
            result: Updates = await self._app.send(
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
            result: Updates = await self._app.send(
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
            await self._app.send(
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
        result: Updates = await self._app.send(
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
            await self._app.send(
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
            await self._app.send(
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
            await self._app.send(
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

    async def toggle_group_call_mute(
        self,
        chat_id: Union[int, str],
        mute: bool,
    ):
        """
        Toggle mute/unmute for the userbot in a group call.

        Args:
            chat_id: The chat ID of the group call.
            mute: If True, mute the userbot. If False, unmute the userbot.
        """
        try:
            await self._app.invoke(
                ToggleGroupCallSettings(
                    call=await self._app.resolve_peer(chat_id),
                    join_muted=mute,
                ),
            )
        except Exception as e:
            py_logger.error(f"Failed to toggle group call mute: {e}")
            raise UnMuteNeeded('Failed to unmute the userbot.')

    def is_connected(self) -> bool:
        return self._app.is_connected

    def no_updates(self):
        return self._app.no_updates

    async def start(self):
        await self._app.start()
