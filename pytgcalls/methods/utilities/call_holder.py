from ntgcalls import StreamStatus

from ...scaffold import Scaffold
from ...types import Call
from ...types.dict import Dict


class CallHolder(Scaffold):
    def __init__(self):
        super().__init__()
        self._conversions = {
            StreamStatus.ACTIVE: Call.Status.ACTIVE,
            StreamStatus.PAUSED: Call.Status.PAUSED,
            StreamStatus.IDLING: Call.Status.IDLE,
        }

    @property
    async def calls(self):
        calls_list = await self._binding.calls()
        return Dict({
            x: Call(
                x, self._conversions[calls_list[x].playback],
                self._conversions[calls_list[x].capture],
            )
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
