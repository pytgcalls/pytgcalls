from typing import Union

from ntgcalls import ConnectionNotFound
from ntgcalls import StreamMode

from ...exceptions import NotInCallError
from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes


class Time(Scaffold):
    @statictypes
    @mtproto_required
    async def time(
        self,
        chat_id: Union[int, str],
        stream_mode: StreamMode = StreamMode.CAPTURE,
    ):
        chat_id = await self.resolve_chat_id(chat_id)
        try:
            return await self._binding.time(chat_id, stream_mode)
        except ConnectionNotFound:
            raise NotInCallError()
