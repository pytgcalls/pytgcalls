from ntgcalls import ConnectionInfo
from ntgcalls import ConnectionState
from ntgcalls import TelegramServerError

from ...scaffold import Scaffold


class HandleConnectionChanged(Scaffold):
    async def _handle_connection_changed(
        self,
        chat_id: int,
        net_state: ConnectionInfo,
    ):
        state = net_state.state
        if state == ConnectionState.CONNECTING:
            return
        if chat_id in self._wait_connect:
            if self._wait_connect[chat_id].done():
                return
            if state == ConnectionState.CONNECTED:
                self._wait_connect[chat_id].set_result(None)
            else:
                self._wait_connect[chat_id].set_exception(
                    TelegramServerError(),
                )
        elif state != ConnectionState.CONNECTED:
            if chat_id > 0:
                await self._app.discard_call(chat_id)
            self._clear_cache(chat_id)
