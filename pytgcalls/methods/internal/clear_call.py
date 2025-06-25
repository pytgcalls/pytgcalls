from ntgcalls import ConnectionNotFound
from ntgcalls import TelegramServerError

from ...scaffold import Scaffold


class ClearCall(Scaffold):
    async def _clear_call(self, chat_id: int):
        if chat_id in self._wait_connect and \
                chat_id not in self._p2p_configs:
            self._wait_connect[chat_id].set_exception(
                TelegramServerError(),
            )
        try:
            await self._binding.stop(chat_id)
        except ConnectionNotFound:
            pass
        self._clear_cache(chat_id)
