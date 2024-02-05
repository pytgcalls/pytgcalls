from typing import Union

from ...exceptions import ClientNotStarted
from ...exceptions import NoActiveGroupCall
from ...exceptions import NoMTProtoClientSet
from ...scaffold import Scaffold
from ...statictypes import statictypes


class ChangeVolumeCall(Scaffold):
    @statictypes
    async def change_volume_call(
        self,
        chat_id: Union[int, str],
        volume: int,
    ):
        if self._app is None:
            raise NoMTProtoClientSet()

        if not self._is_running:
            raise ClientNotStarted()

        chat_id = await self._resolve_chat_id(chat_id)
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
