from ...scaffold import Scaffold
from ...types import Call
from ...types.list import List


class CallHolder(Scaffold):
    @property
    async def calls(self):
        calls_list: dict = await self._binding.calls()  # type: ignore
        return List([
            Call(x, calls_list[x]) for x in calls_list
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
