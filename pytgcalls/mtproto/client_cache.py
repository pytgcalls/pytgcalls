import logging
from time import time
from typing import Any
from typing import List
from typing import Optional

from ..types import Cache
from ..types.chats import GroupCallParticipant
from ..types.participant_list import ParticipantList
from .bridged_client import BridgedClient

py_logger = logging.getLogger('pytgcalls')


class ClientCache:
    def __init__(
        self,
        cache_duration: int,
        app: BridgedClient,
    ):
        self._app: BridgedClient = app
        self._cache_duration = 1 if app.no_updates() else cache_duration
        self._full_chat_cache = Cache()
        self._call_participants_cache = Cache()
        self._phone_calls = Cache()

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

    def set_participants_cache_call(
        self,
        input_id: int,
        participant: GroupCallParticipant,
    ) -> Optional[GroupCallParticipant]:
        chat_id = self.get_chat_id(input_id)
        if chat_id is not None:
            return self._internal_set_participants_cache(
                chat_id,
                participant,
            )
        return None

    def set_participants_cache_chat(
        self,
        chat_id: int,
        call_id: int,
        participant: GroupCallParticipant,
    ) -> Optional[GroupCallParticipant]:
        if self._call_participants_cache.get(chat_id) is None:
            self._call_participants_cache.put(
                chat_id,
                ParticipantList(
                    call_id,
                ),
            )
        return self._internal_set_participants_cache(
            chat_id,
            participant,
        )

    def _internal_set_participants_cache(
        self,
        chat_id: int,
        participant: GroupCallParticipant,
    ) -> Optional[GroupCallParticipant]:
        participants: Optional[
            ParticipantList
        ] = self._call_participants_cache.get(
            chat_id,
        )
        if participants is not None:
            participants.last_mtproto_update = (
                int(time()) + self._cache_duration
            )
            return participants.update_participant(participant)
        return None

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
                    py_logger.debug(
                        'GetParticipant cache miss for %d', chat_id,
                    )
                    try:
                        list_participants = await self._app.get_participants(
                            input_call,
                        )
                        for participant in list_participants:
                            self.set_participants_cache_call(
                                input_call.id,
                                participant,
                            )
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
        for key in self._call_participants_cache.keys:
            participants = self._call_participants_cache.get(key)
            if participants is not None:
                if participants.input_id == input_group_call_id:
                    return key
        return None

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
        if self._call_participants_cache.get(chat_id) is None:
            self._call_participants_cache.put(
                chat_id,
                ParticipantList(
                    input_call.id,
                ),
            )

    def drop_cache(
        self,
        chat_id,
    ) -> None:
        self._full_chat_cache.pop(chat_id)
        self._call_participants_cache.pop(chat_id)

    def set_phone_call(
        self,
        chat_id: int,
        phone_call: Any,
    ) -> None:
        self._phone_calls.put(
            chat_id,
            phone_call,
        )

    def get_phone_call(
        self,
        chat_id: int,
    ) -> Optional[Any]:
        return self._phone_calls.get(chat_id)

    def get_user_id(
        self,
        phone_call_id: int,
    ) -> Optional[int]:
        return next(
            (
                user_id
                for user_id in self._phone_calls.keys
                if self._phone_calls.get(user_id).id == phone_call_id
            ),
            None,
        )

    def drop_phone_call(
        self,
        chat_id: int,
    ) -> None:
        self._phone_calls.pop(chat_id)
