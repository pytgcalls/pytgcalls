from .idle import idle
from ...scaffold import Scaffold


class Run(Scaffold):
    async def run(self):
        await self.start()
        await idle()
