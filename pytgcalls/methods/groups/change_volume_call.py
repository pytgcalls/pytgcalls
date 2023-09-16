from typing import Union

from ...exceptions import ClientNotStarted
from ...exceptions import NoActiveGroupCall
from ...exceptions import NoMTProtoClientSet
from ...scaffold import Scaffold


class ChangeVolumeCall(Scaffold):
    async def change_volume_call(
        self,
        chat_id: Union[int, str],
        volume: int,
    ):
        if self._app is not None:
            if self._is_running:
                chat_id = await self._resolve_chat_id(chat_id)

                chat_call = await self._app.get_full_chat(
                    chat_id,
                )
                if chat_call is not None:
                    await self._app.change_volume(
                        chat_id,
                        volume,
                        self._cache_user_peer.get(chat_id),
                    )
                else:
                    raise NoActiveGroupCall()
            else:
                raise ClientNotStarted()
        else:
            raise NoMTProtoClientSet()
