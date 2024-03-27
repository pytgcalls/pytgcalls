from typing import Union

from ...exceptions import NoActiveGroupCall
from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes


class ChangeVolumeCall(Scaffold):
    @statictypes
    @mtproto_required
    async def change_volume_call(
        self,
        chat_id: Union[int, str],
        volume: int,
    ):
        chat_id = await self.resolve_chat_id(chat_id)
        chat_call = await self._app.get_full_chat(
            chat_id,
        )
        if chat_call is None:
            raise NoActiveGroupCall()

        await self._app.change_volume(
            chat_id,
            volume,
            self._cache_user_peer.get(chat_id),
        )
