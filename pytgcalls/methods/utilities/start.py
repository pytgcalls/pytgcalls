import asyncio

from ...exceptions import PyTgCallsAlreadyRunning
from ...scaffold import Scaffold


class Start(Scaffold):
    async def start(self):
        if not self._is_running:
            self._is_running = True
            loop = asyncio.get_running_loop()
            self._wait_until_run = loop.create_future()
            self._env_checker.check_environment()
            await self._init_mtproto()
            self._handle_mtproto()
            await self._start_binding()
        else:
            raise PyTgCallsAlreadyRunning()
