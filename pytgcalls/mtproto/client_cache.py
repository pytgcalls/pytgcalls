import logging
from time import time
from typing import Any, List
from typing import Optional

from ..types import Cache
from .bridged_client import BridgedClient
from ..types.groups import GroupCallParticipant
from ..types.participant_list import ParticipantList

py_logger = logging.getLogger('pytgcalls')


class ClientCache:
    def __init__(
        self,
        cache_duration: int,
        app: BridgedClient,
    ):
        self._app: BridgedClient = app
        self._cache_duration = cache_duration
        self._full_chat_cache = Cache()
        self._call_participants_cache = Cache()

    async def get_full_chat(
        self,
        chat_id: int,
    ) -> Optional[Any]:
        full_chat = self._full_chat_cache.get(chat_id)
        if full_chat is not None:
            py_logger.debug('FullChat cache hit for %d', chat_id)
            return full_chat
        else:
            # noinspection PyBroadException
            try:
                py_logger.debug('FullChat cache miss for %d', chat_id)
                full_chat = await self._app.get_call(chat_id)
                self.set_cache(
                    chat_id,
                    full_chat,
                )
                return full_chat
            except Exception:
                pass
        return None

    def set_participants_cache(
        self,
        input_id: int,
        user_id: int,
        muted: Optional[bool],
        volume: Optional[int],
        can_self_unmute: Optional[bool],
        video_joined: Optional[bool],
        raised_hand: Optional[int],
        left: Optional[int],
    ) -> Optional[GroupCallParticipant]:
        chat_id = self.get_chat_id(input_id)
        if chat_id is not None:
            participants: Optional[
                ParticipantList
            ] = self._call_participants_cache.get(
                chat_id,
            )
            if participants is not None:
                if not left:
                    return participants.set_participant(
                        user_id,
                        muted,
                        muted != can_self_unmute,
                        video_joined,
                        raised_hand is not None,
                        volume / 100 if volume is not None
                        else 100,
                    )
                else:
                    return participants.remove_participant(
                        user_id,
                        muted,
                        muted != can_self_unmute,
                        video_joined,
                        raised_hand is not None,
                        volume / 100 if volume is not None
                        else 100,
                    )

    async def get_participant_list(
        self,
        chat_id: int,
    ) -> Optional[List[GroupCallParticipant]]:
        input_call = await self.get_full_chat(
            chat_id,
        )
        if input_call is not None:
            participants: Optional[
                ParticipantList
            ] = self._call_participants_cache.get(
                chat_id,
            )
            if participants is not None:
                last_update = participants.last_mtproto_update
                curr_time = int(time())
                if not (last_update - curr_time > 0):
                    py_logger.debug('GetParticipant cache miss for %d', chat_id)
                    try:
                        list_participants = await self._app.get_participants(
                            input_call,
                        )
                        for participant in list_participants:
                            self.set_participants_cache(
                                input_call.id,
                                participant['user_id'],
                                participant['muted'],
                                participant['volume'],
                                participant['can_self_unmute'],
                                participant['video_joined'],
                                participant['raise_hand_rating'],
                                participant['left'],
                            )
                        participants.last_mtproto_update = \
                            curr_time + self._cache_duration
                    except Exception as e:
                        py_logger.error('Error for %s in %d', e, chat_id)
                else:
                    py_logger.debug('GetParticipant cache hit for %d', chat_id)
                return participants.get_participants()
        return []

    def get_chat_id(
        self,
        input_group_call_id: int,
    ) -> Optional[int]:
        for key in self._full_chat_cache.keys():
            input_id = self._full_chat_cache.get(key).id
            if input_id == input_group_call_id:
                return key

    def set_cache(
        self,
        chat_id: int,
        input_call: Any,
    ) -> None:
        self._full_chat_cache.put(
            chat_id,
            input_call,
            self._cache_duration,
        )
        self._call_participants_cache.put(
            chat_id,
            ParticipantList(),
        )

    def drop_cache(
        self,
        chat_id,
    ) -> None:
        self._full_chat_cache.pop(chat_id)
        self._call_participants_cache.pop(chat_id)
