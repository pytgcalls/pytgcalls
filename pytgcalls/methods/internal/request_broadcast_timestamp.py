from ntgcalls import ConnectionError
from ntgcalls import ConnectionNotFound

from ...exceptions import NotInCallError
from ...scaffold import Scaffold


class RequestBroadcastTimestamp(Scaffold):
    async def _request_broadcast_timestamp(
        self,
        chat_id: int,
    ):
        not_in_call = False
        # noinspection PyBroadException
        try:
            time = await self._app.get_stream_timestamp(
                chat_id,
            )
        except NotInCallError:
            time = 0
            not_in_call = True
        except Exception:
            time = 0
        try:
            await self._binding.send_broadcast_timestamp(
                chat_id,
                time,
            )
        except (ConnectionError, ConnectionNotFound):
            pass
        if (
            not_in_call
            and chat_id not in self._wait_connect
            and chat_id not in self._reconnecting
        ):
            self._reconnecting.add(chat_id)
            await self._rejoin_call(chat_id)
