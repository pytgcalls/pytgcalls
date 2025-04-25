from ntgcalls import ConnectionError
from ntgcalls import ConnectionNotFound
from ntgcalls import MediaSegmentStatus
from ntgcalls import SegmentPartRequest

from ...scaffold import Scaffold


class RequestBroadcastPart(Scaffold):
    async def _request_broadcast_part(
        self,
        chat_id: int,
        part_request: SegmentPartRequest,
    ):
        part_status = MediaSegmentStatus.NOT_READY
        # noinspection PyBroadException
        try:
            part = await self._app.download_stream(
                chat_id,
                part_request.timestamp,
                part_request.limit,
                part_request.channel_id
                if part_request.channel_id > 0 else None,
                part_request.quality,
            )
            if part is not None:
                part_status = MediaSegmentStatus.SUCCESS
        except Exception:
            part = None
            part_status = MediaSegmentStatus.RESYNC_NEEDED

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
