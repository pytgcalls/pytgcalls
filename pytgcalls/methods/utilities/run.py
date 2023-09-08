from ...scaffold import Scaffold
from .idle import idle


class Run(Scaffold):
    async def run(self):
        await self.start()
        await idle()
