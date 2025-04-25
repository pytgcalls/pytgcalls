from ntgcalls import ConnectionNotFound
from ntgcalls import TelegramServerError

from ...scaffold import Scaffold


class ClearCall(Scaffold):
    async def _clear_call(self, chat_id: int):
        res = False
        if chat_id in self._wait_connect:
            self._wait_connect[chat_id].set_exception(
                TelegramServerError(),
            )
        try:
            await self._binding.stop(chat_id)
            res = True
        except ConnectionNotFound:
            pass
        self._clear_cache(chat_id)
        return res
