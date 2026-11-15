import asyncio
import logging
from typing import Any

from ..types.chats import GroupCallParticipant
from .bridged_client import BridgedClient
from .group_call import GroupCall

py_logger = logging.getLogger('pytgcalls')


class ClientCache:
    WAIT_FOR_CHANNEL_GET_DIFFERENCE = 1

    def __init__(
        self,
        app: BridgedClient,
    ):
        self._app: BridgedClient = app
        self._calls: dict[int, GroupCall] = {}
        self._phone_calls: dict[int, Any] = {}
        self._dc_calls: dict[int, int] = {}
        self._active_chats: dict[int, int | None] = {}
        self._short_poll: asyncio.Task | None = None

    async def get_input_call(
        self,
        chat_id: int,
    ) -> Any | None:
        if chat_id in self._phone_calls:
            return self._phone_calls[chat_id]
        call = self._calls.get(chat_id)
        if chat_id < 0 and (call is None or self._app.no_updates()):
            # noinspection PyBroadException
            try:
                py_logger.debug('FullChat cache miss for %d', chat_id)
                input_call = await self._app.get_call(chat_id)
                if input_call is None:
                    self.drop_cache(chat_id)
                    return None
                call = self.set_call(chat_id, input_call)
                await call.reload()
            except Exception:
                return None
        if call is None:
            return None
        if call.discarded:
            self.drop_cache(chat_id)
            return None
        if call.schedule_date is not None:
            return None
        return call.input

    async def get_participant_list(
        self,
        chat_id: int,
        sources: list[int] | None = None,
    ) -> list[GroupCallParticipant]:
        if await self.get_input_call(chat_id) is None:
            return []
        call = self._calls.get(chat_id)
        if call is None:
            return []
        if sources:
            await call.apply_last_spoke(sources)
        else:
            if not call.in_call:
                await call.reload_if_stale()
            await call.load_participants()
        return call.participants

    def get_call(
        self,
        chat_id: int | None,
    ) -> GroupCall | None:
        if chat_id is None:
            return None
        return self._calls.get(chat_id)

    def get_chat_id(
        self,
        call_id: int | str,
    ) -> int | None:
        for chat_id, call in self._calls.items():
            if call.id == call_id:
                return chat_id
        return None

    def set_call(
        self,
        chat_id: int,
        input_call: Any,
    ) -> GroupCall:
        self._phone_calls.pop(chat_id, None)
        call = self._calls.get(chat_id)
        if call is None or call.id != GroupCall.call_id(input_call):
            if call is not None:
                call.destroy()
            call = self._calls[chat_id] = GroupCall(
                self._app,
                chat_id,
                input_call,
            )
        return call

    def set_phone_call(
        self,
        user_id: int,
        input_call: Any,
    ) -> None:
        call = self._calls.pop(user_id, None)
        if call is not None:
            call.destroy()
        self._phone_calls[user_id] = input_call

    def set_in_call(
        self,
        chat_id: int,
        in_call: bool,
    ) -> None:
        call = self._calls.get(chat_id)
        if call is None:
            return
        call.in_call = in_call
        if not in_call:
            self._active_chats.pop(chat_id, None)
        elif chat_id < 0 and not self._app.no_updates():
            self._active_chats.setdefault(chat_id, None)
            if self._short_poll is None:
                self._short_poll = asyncio.create_task(
                    self.wait_for_short_poll(),
                )

    async def wait_for_short_poll(self):
        while self._active_chats:
            timeout = None
            for chat_id in list(self._active_chats):
                final = False
                while not final and chat_id in self._active_chats:
                    # noinspection PyBroadException
                    try:
                        pts = self._active_chats[chat_id]
                        if pts is None:
                            pts = await self._app.get_channel_pts(chat_id)
                            if pts is None:
                                self._active_chats.pop(chat_id, None)
                                break
                        difference = await self._app.get_channel_difference(
                            chat_id,
                            pts,
                        )
                        if (
                            difference.__class__.__name__
                            == 'ChannelDifferenceTooLong'
                        ):
                            pts = difference.dialog.pts or pts
                        else:
                            pts = difference.pts
                        if chat_id in self._active_chats:
                            self._active_chats[chat_id] = pts
                        final = bool(difference.final)
                        timeout = min(
                            timeout or difference.timeout or 0,
                            difference.timeout or 0,
                        )
                        await asyncio.sleep(
                            self.WAIT_FOR_CHANNEL_GET_DIFFERENCE,
                        )
                    except Exception as e:
                        flood_wait = getattr(
                            e,
                            'value',
                            getattr(e, 'seconds', None),
                        )
                        await asyncio.sleep(
                            flood_wait
                            if isinstance(flood_wait, int)
                            else self.WAIT_FOR_CHANNEL_GET_DIFFERENCE,
                        )
                        break
            await asyncio.sleep(
                max((timeout or 0) - len(self._active_chats), 0),
            )
        self._short_poll = None

    def drop_cache(
        self,
        chat_id,
    ) -> None:
        call = self._calls.pop(chat_id, None)
        if call is not None:
            call.destroy()
        self._active_chats.pop(chat_id, None)
        self._phone_calls.pop(chat_id, None)
        self._dc_calls.pop(chat_id, None)

    def set_dc_call(
        self,
        chat_id: int,
        dc_id: int,
    ) -> None:
        self._dc_calls[chat_id] = dc_id

    def get_dc_call(
        self,
        chat_id: int,
    ) -> int | None:
        return self._dc_calls.get(chat_id)

    def get_user_id(
        self,
        phone_call_id: int,
    ) -> int | None:
        return next(
            (
                user_id
                for user_id, call in self._phone_calls.items()
                if call.id == phone_call_id
            ),
            None,
        )
