import json
import random
import re
from html import escape
from html import unescape
from typing import Any

from ntgcalls import MediaSegmentQuality
from ntgcalls import Protocol
from ntgcalls import RTCServer
from ntgcalls import SsrcGroup
from ntgcalls import SubchainRequest

from ..handlers import HandlersHolder
from ..types import GroupCallMessage
from ..types import GroupCallParticipant


class BridgedClient(HandlersHolder):
    HTML_TAGS = {
        'MessageEntityBold': 'b',
        'MessageEntityItalic': 'i',
        'MessageEntityUnderline': 'u',
        'MessageEntityStrike': 's',
        'MessageEntitySpoiler': 'tg-spoiler',
        'MessageEntityCode': 'code',
        'MessageEntityCustomEmoji': 'tg-emoji',
    }
    CONFERENCE_ENTITIES = (
        'MessageEntityBold',
        'MessageEntityItalic',
        'MessageEntityUnderline',
        'MessageEntityStrike',
        'MessageEntitySpoiler',
        'MessageEntityCustomEmoji',
    )
    HTML_ALIASES = {
        'strong': 'b',
        'em': 'i',
        'ins': 'u',
        'strike': 's',
        'del': 's',
    }

    e2e_encrypt: Any = None
    e2e_decrypt: Any = None

    def set_e2e(self, encrypt: Any, decrypt: Any):
        self.e2e_encrypt = encrypt
        self.e2e_decrypt = decrypt

    async def get_call(
        self,
        chat_id: int,
    ):
        pass

    async def send_conference_call_broadcast(
        self,
        chat_id: int,
        block: bytes,
    ):
        pass

    async def get_subchain_blocks(
        self,
        chat_id: int,
        subchain_request: SubchainRequest,
    ):
        pass

    async def get_conference_last_block(
        self,
        chat_id: int,
        invite_msg_id: int | None = None,
    ):
        pass

    async def join_group_call(
        self,
        chat_id: int,
        json_join: str,
        video_stopped: bool,
        join_as: Any,
        invite_hash: str | None = None,
        block: bytes | None = None,
        public_key: int | None = None,
        invite_msg_id: int | None = None,
    ):
        pass

    async def create_conference_call(
        self,
        chat_id: int,
        json_join: str,
        video_stopped: bool,
        block: bytes,
        public_key: int,
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
        has_video: bool,
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

    async def close_voice_chat(
        self,
        chat_id: int,
    ):
        pass

    async def get_group_call_participants(
        self,
        chat_id: int,
        sources: list[int] | None = None,
    ):
        pass

    async def change_volume(
        self,
        chat_id: int,
        volume: int,
        participant: Any,
    ):
        pass

    def message_entity(
        self,
        name: str,
        offset: int,
        length: int,
        document_id: int | None,
    ):
        pass

    async def send_group_call_message(
        self,
        chat_id: int,
        text: str,
        stars: int,
        send_as: Any,
    ) -> GroupCallMessage | None:
        pass

    async def delete_group_call_messages(
        self,
        chat_id: int,
        message_ids: list[int],
        report_spam: bool,
    ):
        pass

    async def delete_group_call_participant_messages(
        self,
        chat_id: int,
        participant: Any,
        report_spam: bool,
    ):
        pass

    async def download_stream(
        self,
        chat_id: int,
        timestamp: int,
        limit: int,
        video_channel: int | None,
        video_quality: MediaSegmentQuality,
    ):
        pass

    async def get_stream_timestamp(
        self,
        chat_id: int,
    ):
        pass

    async def set_call_status(
        self,
        chat_id: int,
        muted_status: bool | None,
        video_paused: bool | None,
        video_stopped: bool | None,
        presentation_paused: bool | None,
        participant: Any,
    ):
        pass

    async def get_group_call(
        self,
        input_call: Any,
        limit: int,
    ):
        pass

    async def get_group_participants(
        self,
        input_call: Any,
        sources: list[int],
        offset: str,
        limit: int,
    ):
        pass

    async def get_channel_pts(
        self,
        chat_id: int,
    ):
        pass

    async def get_channel_difference(
        self,
        chat_id: int,
        pts: int,
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

    def set_in_call(self, chat_id: int, in_call: bool):
        pass

    async def start(self):
        pass

    @staticmethod
    def package_name(obj):
        return str(obj.__class__.__module__).split('.')[0]

    @staticmethod
    def parse_source(source) -> GroupCallParticipant.SourceInfo | None:
        if not source or not any(
            source_group.sources for source_group in source.source_groups
        ):
            return None
        return GroupCallParticipant.SourceInfo(
            source.endpoint,
            [
                SsrcGroup(
                    source_group.semantics,
                    [(ssrc & 0xFFFFFFFF) for ssrc in source_group.sources],
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
            bool(participant.video) or bool(participant.presentation),
            bool(participant.presentation),
            bool(participant.video),
            bool(participant.raise_hand_rating),
            participant.volume // 100
            if participant.volume is not None
            else 100,
            participant.source,
            BridgedClient.parse_source(participant.video),
            BridgedClient.parse_source(participant.presentation),
        )

    @staticmethod
    def parse_group_call_message(message) -> GroupCallMessage:
        return GroupCallMessage(
            message.id,
            BridgedClient.chat_id(message.from_id),
            message.message.text,
            BridgedClient.unparse_html(
                message.message.text,
                message.message.entities,
            ),
            message.date,
            message.paid_message_stars or 0,
            bool(message.from_admin),
        )

    @staticmethod
    def unparse_html(text: str, entities: list[Any]) -> str:
        encoded = text.encode('utf-16-le')
        events = []
        for index, entity in enumerate(
            sorted(entities, key=lambda e: (e.offset, -e.length)),
        ):
            tag = BridgedClient.HTML_TAGS.get(entity.__class__.__name__)
            if tag is None:
                continue
            if tag == 'tg-emoji':
                opening = f'<tg-emoji emoji-id="{entity.document_id}">'
            else:
                opening = f'<{tag}>'
            events.append((entity.offset, 1, index, opening))
            events.append(
                (entity.offset + entity.length, 0, -index, f'</{tag}>')
            )
        result = ''
        position = 0
        for offset, _, _, tag in sorted(events):
            result += escape(
                encoded[position * 2 : offset * 2].decode('utf-16-le'),
                quote=False,
            )
            result += tag
            position = offset
        return result + escape(
            encoded[position * 2 :].decode('utf-16-le'),
            quote=False,
        )

    @staticmethod
    def parse_html(
        text: str,
    ) -> tuple[str, list[tuple[str, int, int, int | None]]]:
        names = {tag: name for name, tag in BridgedClient.HTML_TAGS.items()}
        result = ''
        length = 0
        stack: list[tuple[str, int, int | None]] = []
        entities: list[tuple[str, int, int, int | None]] = []
        position = 0
        for match in re.finditer(r'<(/?)([a-zA-Z-]+)([^>]*)>', text):
            segment = unescape(text[position : match.start()])
            result += segment
            length += len(segment.encode('utf-16-le')) // 2
            position = match.end()
            closing, tag, attributes = match.groups()
            tag = BridgedClient.HTML_ALIASES.get(tag.lower(), tag.lower())
            if tag == 'span' and not closing and 'tg-spoiler' in attributes:
                tag = 'tg-spoiler'
            if tag not in names and tag != 'span':
                literal = match.group(0)
                result += literal
                length += len(literal.encode('utf-16-le')) // 2
                continue
            if not closing:
                emoji = re.search(r'emoji-id="?(\d+)', attributes)
                stack.append(
                    (tag, length, int(emoji.group(1)) if emoji else None),
                )
                continue
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == tag or (
                    tag == 'span' and stack[i][0] in ('span', 'tg-spoiler')
                ):
                    opened, start, document_id = stack.pop(i)
                    if opened in names and length > start:
                        entities.append(
                            (
                                names[opened],
                                start,
                                length - start,
                                document_id,
                            ),
                        )
                    break
        segment = unescape(text[position:])
        return result + segment, sorted(entities, key=lambda e: e[1])

    @staticmethod
    def serialize_conference_message(
        random_id: int,
        text: str,
        entities: list[tuple[str, int, int, int | None]],
    ) -> bytes:
        return json.dumps(
            {
                '_': 'groupCallMessage',
                'random_id': str(random_id),
                'message': {
                    '_': 'textWithEntities',
                    'text': text,
                    'entities': [
                        {
                            '_': 'messageEntity' + name[13:],
                            'offset': offset,
                            'length': length,
                            **(
                                {'document_id': str(document_id)}
                                if document_id is not None
                                else {}
                            ),
                        }
                        for name, offset, length, document_id in entities
                    ],
                },
            },
            ensure_ascii=False,
            separators=(',', ':'),
        ).encode()

    @staticmethod
    def deserialize_conference_message(
        data: bytes,
    ) -> tuple[int, str, list[tuple[str, int, int, int | None]]] | None:
        try:
            message = json.loads(data)
            if message.get('_') != 'groupCallMessage':
                return None
            random_id = int(message.get('random_id') or 0)
            content = message['message']
            text = content['text']
            if content.get('_') != 'textWithEntities' or not isinstance(
                text,
                str,
            ):
                return None
            size = len(text.encode('utf-16-le')) // 2
            entities = []
            for entity in content['entities']:
                name = 'MessageEntity' + str(entity.get('_', ''))[13:]
                offset = int(entity.get('offset', -1))
                length = int(entity.get('length', 0))
                if (
                    name not in BridgedClient.CONFERENCE_ENTITIES
                    or offset < 0
                    or length <= 0
                    or offset + length > size
                ):
                    continue
                document_id = None
                if name == 'MessageEntityCustomEmoji':
                    document_id = int(entity.get('document_id') or 0)
                    if not document_id:
                        continue
                entities.append((name, offset, length, document_id))
        except (ValueError, TypeError, KeyError, AttributeError):
            return None
        if not random_id:
            return None
        return random_id, text, entities

    @staticmethod
    def chat_id(input_peer, readable: bool = True) -> int:
        class_name = input_peer.__class__.__name__
        if class_name in ['PeerUser', 'InputPeerUser']:
            return input_peer.user_id
        elif class_name in ['Channel', 'ChannelForbidden']:
            return (
                -1000000000000 - input_peer.id if readable else input_peer.id
            )
        elif hasattr(input_peer, 'channel_id'):
            return (
                -1000000000000 - input_peer.channel_id
                if readable
                else input_peer.channel_id
            )
        elif class_name == 'Chat':
            return -input_peer.id if readable else input_peer.id
        else:
            return -input_peer.chat_id if readable else input_peer.chat_id

    @staticmethod
    def user_from_call(call) -> int:
        class_name = call.__class__.__name__
        if class_name in ['PhoneCallAccepted', 'PhoneCallWaiting']:
            return call.participant_id
        elif class_name in ['PhoneCallRequested', 'PhoneCall']:
            return call.admin_id
        return -1

    @staticmethod
    def parse_servers(servers) -> list[RTCServer]:
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
            )
            if server.__class__.__name__ == 'PhoneConnectionWebrtc'
            else RTCServer(
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
    def parse_quality(quality: MediaSegmentQuality) -> int | None:
        if quality == MediaSegmentQuality.THUMBNAIL:
            return 0
        elif quality == MediaSegmentQuality.MEDIUM:
            return 1
        elif quality == MediaSegmentQuality.FULL:
            return 2
        else:
            return None

    @staticmethod
    def extract_dc(error: str) -> int | None:
        dc_id = re.findall(
            r'('
            r'CALL_MIGRATE_|'
            r'The file to be accessed is currently stored in DC *'
            r')([0-9])',
            error,
        )
        return int(dc_id[0][1]) if dc_id else None

    @staticmethod
    def rnd_id() -> int:
        return random.randint(0, 0x7FFFFFFF - 1)

    async def get_dhc(self):
        pass

    async def get_id(self):
        pass

    async def get_input_call(
        self,
        chat_id: int,
        invite_msg_id: int | None = None,
    ):
        pass
