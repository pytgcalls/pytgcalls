import logging
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
        cache_duration = 0 if app.no_updates() else cache_duration
        full_chat_duration = 1 if app.no_updates() else cache_duration
        self._full_chat_cache = Cache(full_chat_duration)
        self._call_participants_cache = Cache(cache_duration)
        self._dc_call_cache = Cache(full_chat_duration)
        self._phone_calls = Cache(full_chat_duration)

    async def get_full_chat(
        self,
        chat_id: int,
    ) -> Optional[Any]:
        full_chat = self._full_chat_cache.get(chat_id)
        if full_chat is not None:
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
        chat_id: int,
        input_id: int,
        action: GroupCallParticipant.Action,
        participant: GroupCallParticipant,
    ):
        if self._call_participants_cache.get(chat_id) is None:
            self._call_participants_cache.put(
                chat_id,
                ParticipantList(
                    input_id,
                ),
            )
        self._call_participants_cache.get(
            chat_id,
        ).add_participant(
            action,
            participant,
        )

    async def get_participant_list(
        self,
        chat_id: int,
        only_cached: bool = False,
    ) -> List[GroupCallParticipant]:
        input_call = await self.get_full_chat(
            chat_id,
        )
        if input_call is not None:
            if self._call_participants_cache.get(chat_id) is None:
                if only_cached:
                    return []
                py_logger.debug(
                    'GetParticipant cache miss for %d', chat_id,
                )
                list_participants = await self._app.get_participants(
                    input_call,
                )
                for participant in list_participants:
                    self.set_participants_cache(
                        chat_id,
                        input_call.id,
                        GroupCallParticipant.Action.UPDATED,
                        participant,
                    )
            else:
                py_logger.debug('GetParticipant cache hit for %d', chat_id)
            return self._call_participants_cache.get(
                chat_id,
            ).get_participants()
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
        self._dc_call_cache.pop(chat_id)

    def set_dc_call(
        self,
        chat_id: int,
        dc_id: int,
    ) -> None:
        self._dc_call_cache.put(
            chat_id,
            dc_id,
        )

    def get_dc_call(
        self,
        chat_id: int,
    ) -> Optional[int]:
        return self._dc_call_cache.get(chat_id)

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

    def clear(self):
        """Clear all caches to prevent memory leaks"""
        self._full_chat_cache.clear()
        self._call_participants_cache.clear()
        self._dc_call_cache.clear()
        self._phone_calls.clear()

    def cleanup_expired(self) -> int:
        """Cleanup expired entries from all caches"""
        total_cleaned = 0
        total_cleaned += self._full_chat_cache.cleanup_expired()
        total_cleaned += self._call_participants_cache.cleanup_expired()
        total_cleaned += self._dc_call_cache.cleanup_expired()
        total_cleaned += self._phone_calls.cleanup_expired()
        return total_cleaned

    def get_cache_stats(self) -> dict:
        """Get statistics about cache usage"""
        return {
            'full_chat_cache_size': self._full_chat_cache.size(),
            'call_participants_cache_size': self._call_participants_cache.size(),
            'dc_call_cache_size': self._dc_call_cache.size(),
            'phone_calls_cache_size': self._phone_calls.size(),
        }
