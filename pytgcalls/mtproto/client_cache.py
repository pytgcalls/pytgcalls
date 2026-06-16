import logging
from typing import Any
from typing import List
from typing import Optional
from typing import Union

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
        cache_duration = 1 if app.no_updates() else cache_duration
        full_chat_duration = 1 if app.no_updates() else cache_duration
        self._input_calls = Cache(full_chat_duration)
        self._call_participants_cache = Cache(cache_duration)
        self._dc_call_cache = Cache(full_chat_duration)

    async def get_input_call(
        self,
        chat_id: int,
    ) -> Optional[Any]:
        input_call = self._input_calls.get(chat_id)
        if input_call is not None or chat_id > 0:
            return input_call
        else:
            # noinspection PyBroadException
            try:
                py_logger.debug('FullChat cache miss for %d', chat_id)
                input_call = await self._app.get_call(chat_id)
                if input_call is not None:
                    self.set_cache(
                        chat_id,
                        input_call,
                    )
                return input_call
            except Exception:
                pass
        return None

    def set_participants_cache(
        self,
        chat_id: Optional[int],
        action: GroupCallParticipant.Action,
        participant: GroupCallParticipant,
    ) -> Optional[GroupCallParticipant]:
        if chat_id is not None:
            if self._call_participants_cache.get(chat_id) is None:
                self._call_participants_cache.put(
                    chat_id,
                    ParticipantList(),
                )
            participants: Optional[
                ParticipantList
            ] = self._call_participants_cache.get(
                chat_id,
            )
            if participants is not None:
                self._call_participants_cache.update_cache(chat_id)
                return participants.update_participant(
                    action,
                    participant,
                )
        return None

    async def get_participant_list(
        self,
        chat_id: int,
        only_cached: bool = False,
    ) -> List[GroupCallParticipant]:
        input_call = await self.get_input_call(
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
        call_id: Union[int, str],
    ) -> Optional[int]:
        for key in self._input_calls.keys:
            call = self._input_calls.get(key)
            if call is None:
                continue
            if call_id == (call.slug if hasattr(call, 'slug') else call.id):
                self._input_calls.update_cache(key)
                return key
        return None

    def set_cache(
        self,
        chat_id: int,
        input_call: Any,
    ) -> None:
        self._input_calls.put(
            chat_id,
            input_call,
            chat_id > 0,
        )
        if self._call_participants_cache.get(chat_id) is None:
            self._call_participants_cache.put(
                chat_id,
                ParticipantList(),
            )

    def drop_cache(
        self,
        chat_id,
    ) -> None:
        self._input_calls.pop(chat_id)
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

    def get_user_id(
        self,
        phone_call_id: int,
    ) -> Optional[int]:
        return next(
            (
                user_id
                for user_id in self._input_calls.keys
                if getattr(
                    self._input_calls.get(user_id), 'id', None,
                ) == phone_call_id
            ),
            None,
        )
