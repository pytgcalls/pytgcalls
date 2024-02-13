from typing import Union

from ntgcalls import ConnectionNotFound

from ...exceptions import NotInGroupCallError
from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...to_async import ToAsync


class PauseStream(Scaffold):
    @statictypes
    @mtproto_required
    async def pause_stream(
        self,
        chat_id: Union[int, str],
    ):
        chat_id = await self._resolve_chat_id(chat_id)
        try:
            return await ToAsync(
                self._binding.pause,
                chat_id,
            )
        except ConnectionNotFound:
            raise NotInGroupCallError()
