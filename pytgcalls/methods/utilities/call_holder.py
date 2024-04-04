from ntgcalls import StreamStatus

from ...scaffold import Scaffold
from ...types import Call
from ...types.list import List


class CallHolder(Scaffold):
    def __init__(self):
        super().__init__()
        self._conversions = {
            StreamStatus.PLAYING: Call.Status.PLAYING,
            StreamStatus.PAUSED: Call.Status.PAUSED,
            StreamStatus.IDLING: Call.Status.IDLE,
        }

    @property
    async def calls(self):
        calls_list: dict = await self._binding.calls()  # type: ignore
        return List([
            Call(x, self._conversions[calls_list[x]]) for x in calls_list
        ])

    @property
    async def group_calls(self):
        return List([
            x for x in await self.calls if x.chat_id < 0
        ])

    @property
    async def private_calls(self):
        return List([
            x for x in await self.calls if x.chat_id > 0
        ])
