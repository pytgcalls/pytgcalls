import asyncio

from ...exceptions import NoActiveGroupCall
from ...exceptions import NodeJSNotRunning
from ...exceptions import NoMtProtoClientSet
from ...scaffold import Scaffold


class LeaveGroupCall(Scaffold):
    async def leave_group_call(
        self,
        chat_id: int,
    ):
        if self._app is not None:
            if self._wait_until_run is not None:
                chat_call = await self._app.get_full_chat(
                    chat_id,
                )
                if chat_call is not None:
                    async def internal_sender():
                        if not self._wait_until_run.done():
                            await self._wait_until_run
                        await self._binding.send({
                            'action': 'leave_call',
                            'chat_id': chat_id,
                            'type': 'requested',
                        })
                    asyncio.ensure_future(internal_sender())
                else:
                    raise NoActiveGroupCall()
            else:
                raise NodeJSNotRunning()
        else:
            raise NoMtProtoClientSet()
