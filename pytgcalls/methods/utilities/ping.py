from time import time

from ...scaffold import Scaffold
from ...to_async import ToAsync


class Ping(Scaffold):
    @property
    async def ping(self) -> float:
        start_time: float = time()
        await ToAsync(self._binding.ping)

        return round((time() - start_time) * 1000.0, 5)
