from ...scaffold import Scaffold


class Ping(Scaffold):
    @property
    async def ping(self) -> float:
        return await self._binding.ping
