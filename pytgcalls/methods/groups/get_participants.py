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
