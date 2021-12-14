import asyncio

from ...exceptions import NodeJSNotRunning
from ...exceptions import NoMtProtoClientSet
from ...scaffold import Scaffold


class ResumeStream(Scaffold):
    async def resume_stream(
        self,
        chat_id: int,
    ):
        """Resume the paused stream

        This method allow to resume the paused streaming file

        Parameters:
            chat_id (``int``):
                Unique identifier (int) of the target chat.

        Raises:
            NoMtProtoClientSet: In case you try
                to call this method without any MtProto client
            NodeJSNotRunning: In case you try
                to call this method without do
                :meth:`~pytgcalls.PyTgCalls.start` before

        Returns:
            ``bool``:
            On success, true is returned if was resumed

        Example:
            .. code-block:: python
                :emphasize-lines: 10-12

                from pytgcalls import Client
                from pytgcalls import idle
                ...

                app = PyTgCalls(client)
                app.start()

                ...  # Call API methods

                app.resume_stream(
                    -1001185324811,
                )

                idle()
        """
        if self._app is not None:
            if self._wait_until_run is not None:
                async def internal_sender():
                    if not self._wait_until_run.done():
                        await self._wait_until_run
                    await self._binding.send({
                        'action': 'resume',
                        'chat_id': chat_id,
                    })
                active_call = self._call_holder.get_active_call(chat_id)
                asyncio.ensure_future(internal_sender())
                return active_call.status == 'paused'
            else:
                raise NodeJSNotRunning()
        else:
            raise NoMtProtoClientSet()
