import asyncio
import os

from ...exceptions import NodeJSNotRunning
from ...exceptions import PyrogramNotSet
from ...scaffold import Scaffold


class MuteStream(Scaffold):
    async def mute_stream(
        self,
        chat_id: int,
    ):
        if self._app is not None:
            if self._wait_until_run is not None:
                async def internal_sender():
                    if not self._wait_until_run.done():
                        await self._wait_until_run
                    await self._binding.send({
                        'action': 'mute_stream',
                        'chat_id': chat_id,
                    })

                asyncio.ensure_future(internal_sender())
            else:
                raise NodeJSNotRunning()
        else:
            raise PyrogramNotSet()
