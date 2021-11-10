from ...scaffold import Scaffold


class Ping(Scaffold):
    @property
    async def ping(self) -> float:
        return round(await self._binding.ping, 5)
