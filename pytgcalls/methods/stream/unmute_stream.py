from typing import Union

from ntgcalls import ConnectionNotFound

from ...exceptions import NotInGroupCallError
from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...to_async import ToAsync


class UnMuteStream(Scaffold):
    @statictypes
    @mtproto_required
    async def unmute_stream(
        self,
        chat_id: Union[int, str],
    ):
        chat_id = await self._resolve_chat_id(chat_id)
        try:
            return await ToAsync(
                self._binding.unmute,
                chat_id,
            )
        except ConnectionNotFound:
            raise NotInGroupCallError()
