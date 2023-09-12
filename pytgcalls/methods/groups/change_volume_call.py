from typing import Union

from ...exceptions import NoActiveGroupCall, ClientNotStarted
from ...exceptions import NoMtProtoClientSet
from ...mtproto import BridgedClient
from ...scaffold import Scaffold


class ChangeVolumeCall(Scaffold):
    async def change_volume_call(
        self,
        chat_id: Union[int, str],
        volume: int,
    ):
        if self._app is not None:
            if self._is_running:
                try:
                    chat_id = int(chat_id)
                except ValueError:
                    chat_id = BridgedClient.chat_id(
                        await self._app.resolve_peer(chat_id),
                    )

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
            raise NoMtProtoClientSet()
