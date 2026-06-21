from ...scaffold import Scaffold
from ...types import UpdatedEmojis


class HandleEmojisUpdate(Scaffold):
    async def _handle_emojis_update(
        self,
        chat_id: int,
        emojis: str,
    ):
        await self._propagate(
            UpdatedEmojis(
                chat_id,
                emojis,
            ),
            self,
        )
