import asyncio

from ...exceptions import PyTgCallsAlreadyRunning
from ...scaffold import Scaffold


class Start(Scaffold):
    async def start(self):
        if not self._is_running:
            self._is_running = True
            self._wait_until_run = asyncio.Event()
            self._env_checker.check_environment()
            await self._init_pyrogram()
            self._handle_pyrogram()
            await self._start_binding()
        else:
            raise PyTgCallsAlreadyRunning()
