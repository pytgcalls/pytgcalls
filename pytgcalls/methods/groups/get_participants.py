from typing import List
from typing import Optional
from typing import Union

from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...types.groups.group_call_participant import GroupCallParticipant


class GetParticipants(Scaffold):
    async def get_participants(
        self,
        chat_id: Union[int, str],
    ) -> Optional[List[GroupCallParticipant]]:
        """Get list of participants from a group call

        This method return the list of participants on a group call
        using MtProto APIs

        Parameters:
            chat_id (``int`` | ``str``):
                Can be a direct id (int) or a username (str)

        Returns:
            List of :obj:`~pytgcalls.types.GroupCallParticipant()`:
            On success, a list of participants is returned

        Example:
            .. code-block:: python
                :emphasize-lines: 10-12

                from pytgcalls import Client
                from pytgcalls import idle
                ...

                app = PyTgCalls(client)
                app.start()

                ...  # Call API methods

                app.get_participants(
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
        self._call_holder.get_call(
            chat_id,
        )
        return await self._app.get_group_call_participants(
            chat_id,
        )
