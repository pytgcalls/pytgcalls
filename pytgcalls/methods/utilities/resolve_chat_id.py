from typing import Union

from ...mtproto import BridgedClient
from ...scaffold import Scaffold


class ResolveChatID(Scaffold):
    async def resolve_chat_id(self, chat_id: Union[int, str]) -> int:
        try:
            return int(chat_id)
        except ValueError:
            return BridgedClient.chat_id(
                await self._app.resolve_peer(chat_id),
            )
