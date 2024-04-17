from typing import Union

from ntgcalls import ConnectionNotFound

from ...exceptions import NotInCallError
from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes


class PlayedTime(Scaffold):
    @statictypes
    @mtproto_required
    async def played_time(
        self,
        chat_id: Union[int, str],
    ):
        chat_id = await self.resolve_chat_id(chat_id)
        try:
            return await self._binding.time(chat_id)
        except ConnectionNotFound:
            raise NotInCallError()
