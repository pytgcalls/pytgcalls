from typing import Union

from ntgcalls import ConnectionError

from ...exceptions import NoMtProtoClientSet
from ...exceptions import NotInGroupCallError
from ...scaffold import Scaffold
from ...to_async import ToAsync


class PlayedTime(Scaffold):
    async def played_time(
        self,
        chat_id: Union[int, str],
    ):
        chat_id = await self._resolve_chat_id(chat_id)

        if self._app is not None:
            try:
                return await ToAsync(
                    self._binding.time,
                    chat_id,
                )
            except ConnectionError:
                raise NotInGroupCallError()
        else:
            raise NoMtProtoClientSet()
