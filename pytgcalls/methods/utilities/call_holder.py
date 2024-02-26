from typing import Union

from ntgcalls import StreamStatus

from ...exceptions import GroupCallNotFound
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...types.groups.group_call import GroupCall
from ...types.list import List


class CallHolder(Scaffold):
    PLAYING = 1
    PAUSED = 2
    IDLE = 3

    def __init__(self):
        super().__init__()
        self._conversions = {
            StreamStatus.Playing: self.PLAYING,
            StreamStatus.Paused: self.PAUSED,
            StreamStatus.Idling: self.IDLE,
        }

    @property
    def calls(self):
        calls_list: dict = self._binding.calls()  # type: ignore
        return List([
            GroupCall(x, self._conversions[calls_list[x]]) for x in calls_list
        ])

    @property
    def active_calls(self):
        calls_list: dict = self._binding.calls()  # type: ignore
        return List([
            GroupCall(x, self._conversions[calls_list[x]]) for x in calls_list
            if calls_list[x] != StreamStatus.Idling
        ])

    @statictypes
    async def get_active_call(
        self,
        chat_id: Union[int, str],
    ):
        calls_list: dict = self._binding.calls()
        int_id = await self._resolve_chat_id(chat_id)

        if int_id in calls_list:
            if calls_list[int_id] != StreamStatus.Idling:
                return GroupCall(
                    int_id, self._conversions[calls_list[int_id]],
                )

        raise GroupCallNotFound(int_id)

    @statictypes
    async def get_call(
        self,
        chat_id: int,
    ):
        calls_list: dict = self._binding.calls()
        chat_id = await self._resolve_chat_id(chat_id)

        if chat_id in calls_list:
            return GroupCall(chat_id, self._conversions[calls_list[chat_id]])

        raise GroupCallNotFound(chat_id)
