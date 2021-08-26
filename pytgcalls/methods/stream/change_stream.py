import asyncio
import os

from ...exceptions import NodeJSNotRunning
from ...exceptions import PyrogramNotSet
from ...scaffold import Scaffold


class ChangeStream(Scaffold):
    async def change_stream(
        self,
        chat_id: int,
        file_path: str,
    ):
        if self._app is not None:
            if self._wait_until_run is not None:
                if os.path.isfile(file_path):
                    async def internal_sender():
                        if not self._wait_until_run.done():
                            await self._wait_until_run
                        await self._binding.send({
                            'action': 'change_stream',
                            'chat_id': chat_id,
                            'file_path': file_path,
                        })
                    asyncio.ensure_future(internal_sender())
                else:
                    raise FileNotFoundError()
            else:
                raise NodeJSNotRunning()
        else:
            raise PyrogramNotSet()
