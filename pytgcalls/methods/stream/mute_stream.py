from typing import Union

from ntgcalls import ConnectionError

from ...exceptions import ClientNotStarted
from ...exceptions import NoMTProtoClientSet
from ...exceptions import NotInGroupCallError
from ...scaffold import Scaffold
from ...to_async import ToAsync


class MuteStream(Scaffold):
    async def mute_stream(
        self,
        chat_id: Union[int, str],
    ):
        chat_id = await self._resolve_chat_id(chat_id)

        if self._app is not None:
            if self._is_running:
                try:
                    return await ToAsync(
                        self._binding.mute,
                        chat_id,
                    )
                except ConnectionError:
                    raise NotInGroupCallError()
            else:
                raise ClientNotStarted()
        else:
            raise NoMTProtoClientSet()
