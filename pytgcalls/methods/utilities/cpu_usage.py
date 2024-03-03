from ...scaffold import Scaffold
from ...to_async import ToAsync


class CpuUsage(Scaffold):
    @property
    async def cpu_usage(self) -> float:
        return await ToAsync(
            self.loop,
            self._binding.cpuUsage,
        )
