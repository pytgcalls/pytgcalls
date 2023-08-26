from typing import Union

from ntgcalls import ConnectionError
from ...exceptions import NoMtProtoClientSet
from ...exceptions import NotInGroupCallError
from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...to_async import ToAsync


class PlayedTime(Scaffold):
    async def played_time(
        self,
        chat_id: Union[int, str],
    ):
        """Get the played time of the stream

        This method allows you to get the played time of the stream

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier of the target chat.
                Can be a direct id (int) or a username (str)

        Raises:
            NoMtProtoClientSet: In case you try
                to call this method without any MtProto client
            NoActiveGroupCall: In case you try
                to edit a not started group call
        """
        try:
            chat_id = int(chat_id)
        except ValueError:
            chat_id = BridgedClient.chat_id(
                await self._app.resolve_peer(chat_id),
            )

        if self._app is not None:
            try:
                return await ToAsync(
                    self._binding.time,
                    chat_id
                )
            except ConnectionError:
                raise NotInGroupCallError()
        else:
            raise NoMtProtoClientSet()
