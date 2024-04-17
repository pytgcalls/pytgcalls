from typing import List
from typing import Optional
from typing import Union

from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...types.chats import GroupCallParticipant


class GetParticipants(Scaffold):
    @statictypes
    @mtproto_required
    async def get_participants(
        self,
        chat_id: Union[int, str],
    ) -> Optional[List[GroupCallParticipant]]:
        return await self._app.get_group_call_participants(
            await self.resolve_chat_id(chat_id),
        )
