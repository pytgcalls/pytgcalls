import asyncio

from ...exceptions import NodeJSNotRunning, PyrogramNotSet
from ...scaffold import Scaffold


class PauseStream(Scaffold):
    async def pause_stream(
        self,
        chat_id: int,
    ):
        if self._app is not None:
            if self._binding.is_alive() or \
                        self._wait_until_run is not None:
                async def internal_sender():
                    await self._wait_until_run.wait()
                    await asyncio.sleep(0.06)
                    await self._binding.send({
                        'action': 'pause',
                        'chat_id': chat_id,
                    })
                asyncio.ensure_future(internal_sender())
            else:
                raise NodeJSNotRunning()
        else:
            raise PyrogramNotSet()
