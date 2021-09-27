from typing import Optional, List

from ...scaffold import Scaffold
from ...types.groups.group_call_participant import GroupCallParticipant


class GetParticipants(Scaffold):
    async def get_participants(
        self,
        chat_id: int,
    ) -> Optional[List[GroupCallParticipant]]:
        self._call_holder.get_call(
            chat_id,
        )
        return await self._app.get_group_call_participants(
            chat_id,
        )
