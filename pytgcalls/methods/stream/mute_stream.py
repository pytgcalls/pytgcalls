from typing import Union

from ntgcalls import ConnectionError

from ...exceptions import NoMtProtoClientSet
from ...exceptions import NotInGroupCallError
from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...to_async import ToAsync


class MuteStream(Scaffold):
    async def mute_stream(
        self,
        chat_id: Union[int, str],
    ):
        try:
            chat_id = int(chat_id)
        except ValueError:
            chat_id = BridgedClient.chat_id(
                await self._app.resolve_peer(chat_id),
            )

        if self._app is not None:
            try:
                return await ToAsync(
                    self._binding.mute,
                    chat_id,
                )
            except ConnectionError:
                raise NotInGroupCallError()
        else:
            raise NoMtProtoClientSet()
