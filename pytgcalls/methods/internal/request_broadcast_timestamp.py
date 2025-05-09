from ntgcalls import ConnectionError
from ntgcalls import ConnectionNotFound

from ...scaffold import Scaffold


class RequestBroadcastTimestamp(Scaffold):
    async def _request_broadcast_timestamp(
        self,
        chat_id: int,
    ):
        # noinspection PyBroadException
        try:
            time = await self._app.get_stream_timestamp(
                chat_id,
            )
        except Exception:
            time = 0
        try:
            await self._binding.send_broadcast_timestamp(
                chat_id,
                time,
            )
        except (ConnectionError, ConnectionNotFound):
            pass
