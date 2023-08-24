from typing import Union

from ntgcalls import ConnectionError
from ...to_async import ToAsync
from ...exceptions import NoActiveGroupCall, NotInGroupCallError
from ...exceptions import NoMtProtoClientSet
from ...mtproto import BridgedClient
from ...scaffold import Scaffold


class LeaveGroupCall(Scaffold):
    async def leave_group_call(
        self,
        chat_id: Union[int, str],
    ):
        """Leave a group call

        This method allow to leave a Group Call

        Parameters:
             chat_id (``int`` | ``str``):
                Unique identifier of the target chat.
                Can be a direct id (int) or a username (str)

        Raises:
            NoMtProtoClientSet: In case you try
                to call this method without any MtProto client
            NoActiveGroupCall: In case you try
                to edit a not started group call
            NotInGroupCallError: In case you try
                to leave a non-joined group call

        Example:
            .. code-block:: python
                :emphasize-lines: 10-12

                from pytgcalls import Client
                from pytgcalls import idle
                ...

                app = PyTgCalls(client)
                app.start()

                ...  # Call API methods

                app.leave_group_call(
                    -1001185324811,
                )

                idle()
        """
        if self._app is not None:
            try:
                chat_id = int(chat_id)
            except ValueError:
                chat_id = BridgedClient.chat_id(
                    await self._app.resolve_peer(chat_id),
                )

            chat_call = await self._app.get_full_chat(
                chat_id,
            )

            if chat_call is not None:
                try:
                    await ToAsync(
                        self._binding.stop(chat_id)
                    )
                except ConnectionError:
                    raise NotInGroupCallError()
                else:
                    raise NoActiveGroupCall()
            else:
                raise NoMtProtoClientSet()
