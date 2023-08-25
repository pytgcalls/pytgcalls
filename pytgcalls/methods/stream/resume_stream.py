from typing import Union

from ntgcalls import ConnectionError
from ...to_async import ToAsync
from ...exceptions import NoMtProtoClientSet
from ...exceptions import NotInGroupCallError
from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...types import NotInGroupCall


class ResumeStream(Scaffold):
    async def resume_stream(
        self,
        chat_id: Union[int, str],
    ):
        """Resume the paused stream

        This method allow to resume the paused streaming file

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
            NotInGroupCallError: In case you try
                to leave a non-joined group call

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
        try:
            chat_id = int(chat_id)
        except ValueError:
            chat_id = BridgedClient.chat_id(
                await self._app.resolve_peer(chat_id),
            )

        if self._app is not None:
            try:
                return await ToAsync(
                    self._binding.resume,
                    chat_id
                )
            except ConnectionError:
                raise NotInGroupCallError()
        else:
            raise NoMtProtoClientSet()
