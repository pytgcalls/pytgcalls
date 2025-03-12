from typing import List
from typing import Optional
from typing import Union

from ...exceptions import UnsupportedMethod
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
        chat_id = await self.resolve_chat_id(chat_id)
        if chat_id >= 0:  # type: ignore
            raise UnsupportedMethod()
        return await self._app.get_group_call_participants(
            chat_id,
        )
