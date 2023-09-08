from typing import Union

from ...mtproto import BridgedClient
from ...scaffold import Scaffold


class GetActiveCall(Scaffold):
    async def get_active_call(
        self,
        chat_id: Union[int, str],
    ):
        try:
            chat_id = int(chat_id)
        except ValueError:
            chat_id = BridgedClient.chat_id(
                await self._app.resolve_peer(chat_id),
            )
        return self._call_holder.get_active_call(
            chat_id,
        )
