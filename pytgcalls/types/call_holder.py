from typing import Dict

from ..exceptions import GroupCallNotFound
from .groups import GroupCall
from .list import List


class CallHolder:
    PLAYING = 1
    PAUSED = 2
    IDLE = 3

    def __init__(self):
        self._calls: Dict[int, int] = {}

    def set_status(
        self,
        chat_id: int,
        status: int,
    ):
        self._calls[chat_id] = status

    @property
    def active_calls(self):
        return List([
            GroupCall(x, self._calls[x]) for x in self._calls
            if self._calls[x] != self.IDLE
        ])

    @property
    def calls(self):
        return List([
            GroupCall(x, self._calls[x]) for x in self._calls
        ])

    def get_active_call(
        self,
        chat_id: int,
    ):
        if chat_id in self._calls:
            if self._calls[chat_id] != self.IDLE:
                return GroupCall(chat_id, self._calls[chat_id])
        raise GroupCallNotFound(chat_id)

    def get_call(
        self,
        chat_id: int,
    ):
        if chat_id in self._calls:
            return GroupCall(chat_id, self._calls[chat_id])
        raise GroupCallNotFound(chat_id)

    def remove_call(
        self,
        chat_id: int,
    ):
        if chat_id in self._calls:
            del self._calls[chat_id]
