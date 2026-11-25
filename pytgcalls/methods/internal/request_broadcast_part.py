from ntgcalls import ConnectionError
from ntgcalls import ConnectionNotFound
from ntgcalls import MediaSegmentPartStatus
from ntgcalls import SegmentPartRequest

from ...exceptions import NotInCallError
from ...scaffold import Scaffold


class RequestBroadcastPart(Scaffold):
    async def _request_broadcast_part(
        self,
        chat_id: int,
        part_request: SegmentPartRequest,
    ):
        part_status = MediaSegmentPartStatus.NOT_READY
        not_in_call = False
        # noinspection PyBroadException
        try:
            part = await self._app.download_stream(
                chat_id,
                part_request.timestamp,
                part_request.limit,
                part_request.channel_id
                if part_request.channel_id > 0
                else None,
                part_request.quality,
            )
            if part is not None:
                part_status = MediaSegmentPartStatus.SUCCESS
        except NotInCallError:
            part = None
            part_status = MediaSegmentPartStatus.RESYNC_NEEDED
            not_in_call = True
        except Exception:
            part = None
            part_status = MediaSegmentPartStatus.RESYNC_NEEDED

        try:
            await self._binding.send_broadcast_part(
                chat_id,
                part_request.segment_id,
                part_request.part_id,
                part_status,
                part_request.quality_update,
                part,
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
