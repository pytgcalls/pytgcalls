from ...scaffold import Scaffold


class CpuUsage(Scaffold):
    @property
    async def cpu_usage(self) -> float:
        return await self._binding.cpu_usage()
