from typing import Union

from ntgcalls import ConnectionNotFound

from ...exceptions import ClientNotStarted
from ...exceptions import NoMTProtoClientSet
from ...exceptions import NotInGroupCallError
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...to_async import ToAsync


class PauseStream(Scaffold):
    @statictypes
    async def pause_stream(
        self,
        chat_id: Union[int, str],
    ):
        if self._app is None:
            raise NoMTProtoClientSet()

        if not self._is_running:
            raise ClientNotStarted()

        chat_id = await self._resolve_chat_id(chat_id)
        try:
            status = await ToAsync(
                self._binding.pause,
                chat_id,
            )
            return status
        except ConnectionNotFound:
            raise NotInGroupCallError()
