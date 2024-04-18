from ntgcalls import StreamStatus

from ...scaffold import Scaffold
from ...types import Call
from ...types.dict import Dict


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
        calls_list = await self._binding.calls()
        return Dict({
            x: Call(x, self._conversions[calls_list[x]])
            for x in calls_list
        })

    @property
    async def group_calls(self):
        return Dict({
            chat_id: x
            for chat_id, x in (await self.calls).items() if chat_id < 0
        })

    @property
    async def private_calls(self):
        return Dict({
            chat_id: x
            for chat_id, x in (await self.calls).items() if chat_id > 0
        })
