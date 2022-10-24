from typing import Union

from ...mtproto import BridgedClient
from ...scaffold import Scaffold


class GetActiveCall(Scaffold):
    async def get_active_call(
        self,
        chat_id: Union[int, str],
    ):
        """Check/Get an active call

        This method check if is active a Group Call (Playing / Paused),
        if not, this can raise an error

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier of the target chat.
                Can be a direct id (int) or a username (str)

        Raises:
            GroupCallNotFound: In case you try
                to get a non-existent group call

        Returns:
            :obj:`~pytgcalls.types.GroupCall()`: On success,
            the group call is returned.

        Example:
            .. code-block:: python
                :emphasize-lines: 10-12

                from pytgcalls import Client
                from pytgcalls import idle
                ...

                app = PyTgCalls(client1)
                app.start()

                ...  # Call API methods

                app.get_active_call(
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
        return self._call_holder.get_active_call(
            chat_id,
        )
