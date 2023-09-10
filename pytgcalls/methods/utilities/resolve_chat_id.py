from typing import Union

from ...mtproto import BridgedClient
from ...scaffold import Scaffold


class ResolveChatID(Scaffold):
    async def _resolve_chat_id(self, chat_id: Union[int, str]) -> int:
        try:
            chat_id = int(chat_id)
        except ValueError:
            chat_id = BridgedClient.chat_id(
                await self._app.resolve_peer(chat_id),
            )

        return chat_id
