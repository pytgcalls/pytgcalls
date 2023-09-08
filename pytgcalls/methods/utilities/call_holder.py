from ntgcalls import StreamStatus

from ...exceptions import GroupCallNotFound
from ...scaffold import Scaffold
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
        calls = self._binding.calls()
        return List([
            GroupCall(x, self._conversions[calls[x]]) for x in calls
        ])

    @property
    def active_calls(self):
        calls = self._binding.calls()
        return List([
            GroupCall(x, self._conversions[calls[x]]) for x in calls
            if self._binding.calls()[x] != StreamStatus.Idling
        ])

    def get_active_call(
        self,
        chat_id: int,
    ):
        calls = self._binding.calls()
        if chat_id in calls:
            if calls[chat_id] != StreamStatus.Idling:
                return GroupCall(chat_id, self._conversions[calls[chat_id]])

        raise GroupCallNotFound(chat_id)

    def get_call(
        self,
        chat_id: int,
    ):
        calls = self._binding.calls()
        if chat_id in calls:
            return GroupCall(chat_id, self._conversions[calls[chat_id]])

        raise GroupCallNotFound(chat_id)
