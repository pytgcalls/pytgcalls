import asyncio

from ntgcalls import ConnectionInfo
from ntgcalls import ConnectionKind
from ntgcalls import ConnectionState
from ntgcalls import TelegramServerError

from ...scaffold import Scaffold


class HandleConnectionChanged(Scaffold):
    CHECK_JOINED_TIMEOUT = 4

    async def _handle_connection_changed(
        self,
        chat_id: int,
        net_state: ConnectionInfo,
    ):
        state = net_state.state
        if state == ConnectionState.CONNECTING:
            if (
                chat_id > 0
                or net_state.kind != ConnectionKind.NORMAL
                or chat_id in self._wait_connect
                or chat_id in self._reconnecting
            ):
                return
            self._reconnecting.add(chat_id)
            while chat_id in self._reconnecting:
                await asyncio.sleep(self.CHECK_JOINED_TIMEOUT)
                if chat_id not in self._reconnecting:
                    break
                # noinspection PyBroadException
                try:
                    joined = await self._app.check_group_call(chat_id)
                except Exception:
                    joined = False
                if not joined:
                    await self._rejoin_call(chat_id)
            return
        if (
            state == ConnectionState.CONNECTED
            and net_state.kind == ConnectionKind.NORMAL
        ):
            self._reconnecting.discard(chat_id)
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
