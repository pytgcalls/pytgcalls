import asyncio
from typing import Union

from ...exceptions import NodeJSNotRunning
from ...exceptions import NoMtProtoClientSet
from ...exceptions import NotInGroupCallError
from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...types import NotInGroupCall
from ...types.session import Session
from ...types.stream import StreamTime


class PlayedTime(Scaffold):
    async def played_time(
        self,
        chat_id: Union[int, str],
    ):
        """Get the played time of the stream

        This method allow to get the played time of the stream

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier of the target chat.
                Can be a direct id (int) or a username (str)

        Raises:
            NoMtProtoClientSet: In case you try
                to call this method without any MtProto client
            NodeJSNotRunning: In case you try
                to call this method without do
                :meth:`~pytgcalls.PyTgCalls.start` before
            NoActiveGroupCall: In case you try
                to edit a not started group call
        """
        try:
            chat_id = int(chat_id)
        except ValueError:
            chat_id = BridgedClient.chat_id(
                await self._app.resolve_peer(chat_id),
            )
        if self._app is not None:
            if self._wait_until_run is not None:
                solver_id = Session.generate_session_id(24)

                async def internal_sender():
                    if not self._wait_until_run.done():
                        await self._wait_until_run
                    request = {
                        'action': 'played_time',
                        'chat_id': chat_id,
                        'solver_id': solver_id,
                    }
                    await self._binding.send(request)

                asyncio.ensure_future(internal_sender())
                result = await self._wait_result.wait_future_update(
                    solver_id,
                )
                if isinstance(result, NotInGroupCall):
                    raise NotInGroupCallError()
                elif isinstance(result, StreamTime):
                    return result.time
            else:
                raise NodeJSNotRunning()
        else:
            raise NoMtProtoClientSet()
