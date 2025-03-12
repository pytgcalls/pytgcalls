from typing import Union

from ntgcalls import ConnectionNotFound

from ...exceptions import NotInCallError
from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...types import Direction


class Time(Scaffold):
    @statictypes
    @mtproto_required
    async def time(
        self,
        chat_id: Union[int, str],
        direction: Direction = Direction.OUTGOING,
    ):
        chat_id = await self.resolve_chat_id(chat_id)
        try:
            return await self._binding.time(chat_id, direction.to_raw())
        except ConnectionNotFound:
            raise NotInCallError()
