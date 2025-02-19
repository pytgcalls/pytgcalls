import json
from typing import List
from typing import Optional
from typing import Union

from ntgcalls import Protocol
from telethon import TelegramClient
from telethon.errors import ChannelPrivateError
from telethon.events import Raw
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetDhConfigRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.phone import AcceptCallRequest
from telethon.tl.functions.phone import ConfirmCallRequest
from telethon.tl.functions.phone import CreateGroupCallRequest
from telethon.tl.functions.phone import DiscardCallRequest
from telethon.tl.functions.phone import EditGroupCallParticipantRequest
from telethon.tl.functions.phone import GetGroupCallRequest
from telethon.tl.functions.phone import GetGroupParticipantsRequest
from telethon.tl.functions.phone import JoinGroupCallPresentationRequest
from telethon.tl.functions.phone import JoinGroupCallRequest
from telethon.tl.functions.phone import LeaveGroupCallPresentationRequest
from telethon.tl.functions.phone import LeaveGroupCallRequest
from telethon.tl.functions.phone import RequestCallRequest
from telethon.tl.functions.phone import SendSignalingDataRequest
from telethon.tl.types import ChatForbidden
from telethon.tl.types import DataJSON
from telethon.tl.types import GroupCall
from telethon.tl.types import GroupCallDiscarded
from telethon.tl.types import InputChannel
from telethon.tl.types import InputGroupCall
from telethon.tl.types import InputPeerChannel
from telethon.tl.types import InputPhoneCall
from telethon.tl.types import MessageActionChatDeleteUser
from telethon.tl.types import MessageActionInviteToGroupCall
from telethon.tl.types import MessageService
from telethon.tl.types import PeerChannel
from telethon.tl.types import PeerChat
from telethon.tl.types import PhoneCall
from telethon.tl.types import PhoneCallAccepted
from telethon.tl.types import PhoneCallDiscarded
from telethon.tl.types import PhoneCallDiscardReasonHangup
from telethon.tl.types import PhoneCallDiscardReasonMissed
from telethon.tl.types import PhoneCallProtocol
from telethon.tl.types import PhoneCallRequested
from telethon.tl.types import PhoneCallWaiting
from telethon.tl.types import TypeInputChannel
from telethon.tl.types import TypeInputPeer
from telethon.tl.types import TypeInputUser
from telethon.tl.types import UpdateChannel
from telethon.tl.types import UpdateGroupCall
from telethon.tl.types import UpdateGroupCallConnection
from telethon.tl.types import UpdateGroupCallParticipants
from telethon.tl.types import UpdateNewChannelMessage
from telethon.tl.types import UpdateNewMessage
from telethon.tl.types import UpdatePhoneCall
from telethon.tl.types import UpdatePhoneCallSignalingData
from telethon.tl.types import Updates
from telethon.tl.types.messages import DhConfig

from ..types import CallProtocol
from ..types import ChatUpdate
from ..types import GroupCallParticipant
from ..types import RawCallUpdate
from ..types import UpdatedGroupCallParticipant
from .bridged_client import BridgedClient
from .client_cache import ClientCache


class TelethonClient(BridgedClient):
    def __init__(
        self,
        cache_duration: int,
        client: TelegramClient,
    ):
        super().__init__()
        self._app: TelegramClient = client
        self._cache: ClientCache = ClientCache(
            cache_duration,
            self,
        )

        @self._app.on(Raw())
        async def on_update(update):
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
                chat_id = self.chat_id(
                    await self._get_entity_group(
                        update.chat_id,
                    ),
                )
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
                    self._cache.drop_cache(
                        chat_id,
                    )
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
                try:
                    await self._app.get_entity(
                        PeerChannel(chat_id),
                    )
                except ChannelPrivateError:
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
                        await self.propagate(
                            ChatUpdate(
                                chat_id,
                                ChatUpdate.Status.INVITED_VOICE_CHAT,
                                update.message.action,
                            ),
                        )
                    if isinstance(update.message.out, bool):
                        if update.message.out:
                            self._cache.drop_cache(chat_id)
                            await self.propagate(
                                ChatUpdate(
                                    chat_id,
                                    ChatUpdate.Status.LEFT_GROUP,
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
                                await self._app.get_entity(chat_id),
                                ChatForbidden,
                            ):
                                self._cache.drop_cache(chat_id)
                                await self.propagate(
                                    ChatUpdate(
                                        chat_id,
                                        ChatUpdate.Status.KICKED,
                                    ),
                                )

    async def _get_entity_group(self, chat_id):
        try:
            return await self._app.get_entity(
                PeerChannel(chat_id),
            )
        except ValueError:
            return await self._app.get_entity(
                PeerChat(chat_id),
            )

    async def get_call(
        self,
        chat_id: int,
    ) -> Optional[InputGroupCall]:
        chat = await self._app.get_input_entity(chat_id)
        if isinstance(chat, InputPeerChannel):
            input_call = (
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
            input_call = (
                await self._app(
                    GetFullChatRequest(chat_id),
                )
            ).full_chat.call

        if input_call is not None:
            raw_call = (
                await self._app(
                    GetGroupCallRequest(
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
        return await self._app(
            GetDhConfigRequest(
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
            result = await self._app(
                GetGroupParticipantsRequest(
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
        join_as: TypeInputPeer,
    ) -> str:
        chat_call = await self._cache.get_full_chat(chat_id)
        if chat_call is not None:
            result: Updates = await self._app(
                JoinGroupCallRequest(
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
            result: Updates = await self._app(
                JoinGroupCallPresentationRequest(
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
            await self._app(
                LeaveGroupCallPresentationRequest(
                    call=chat_call,
                ),
            )

    async def request_call(
        self,
        user_id: int,
        g_a_hash: bytes,
        protocol: Protocol,
    ):
        return await self._app(
            RequestCallRequest(
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
        return await self._app(
            AcceptCallRequest(
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
            await self._app(
                ConfirmCallRequest(
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
        await self._app(
            SendSignalingDataRequest(
                peer=self._cache.get_phone_call(user_id),
                data=data,
            ),
        )

    async def create_group_call(
        self,
        chat_id: int,
    ):
        result: Updates = await self._app(
            CreateGroupCallRequest(
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
            await self._app(
                LeaveGroupCallRequest(
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
        await self._app(
            DiscardCallRequest(
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

    async def set_call_status(
        self,
        chat_id: int,
        muted_status: Optional[bool],
        video_paused: Optional[bool],
        video_stopped: Optional[bool],
        presentation_paused: Optional[bool],
        participant: TypeInputPeer,
    ):
        chat_call = await self._cache.get_full_chat(chat_id)
        if chat_call is not None:
            await self._app(
                EditGroupCallParticipantRequest(
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

    @staticmethod
    def parse_protocol(protocol: Protocol) -> PhoneCallProtocol:
        return PhoneCallProtocol(
            min_layer=protocol.min_layer,
            max_layer=protocol.max_layer,
            udp_p2p=protocol.udp_p2p,
            udp_reflector=protocol.udp_reflector,
            library_versions=protocol.library_versions,
        )

    async def resolve_peer(
        self,
        user_id: Union[int, str],
    ) -> Union[TypeInputPeer, TypeInputUser, TypeInputChannel]:
        return await self._app.get_input_entity(user_id)

    async def get_id(self) -> int:
        return (await self._app.get_me()).id

    def is_connected(self) -> bool:
        return self._app.is_connected()

    def no_updates(self):
        return False

    # noinspection PyUnresolvedReferences
    async def start(self):
        await self._app.start()
