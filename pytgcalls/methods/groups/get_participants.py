from typing import List
from typing import Optional
from typing import Union

from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...types.groups import GroupCallParticipant


class GetParticipants(Scaffold):
    @statictypes
    async def get_participants(
        self,
        chat_id: Union[int, str],
    ) -> Optional[List[GroupCallParticipant]]:

        int_id = await self._resolve_chat_id(chat_id)
        await self.get_call(int_id)

        return await self._app.get_group_call_participants(
            int_id,
        )
