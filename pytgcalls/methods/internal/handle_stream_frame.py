from typing import List

from ntgcalls import Frame as RawFrame
from ntgcalls import StreamDevice
from ntgcalls import StreamMode

from ...scaffold import Scaffold
from ...types import Device
from ...types import Direction
from ...types import Frame
from ...types import StreamFrames


class HandleStreamFrame(Scaffold):
    async def _handle_stream_frame(
        self,
        chat_id: int,
        mode: StreamMode,
        device: StreamDevice,
        frames: List[RawFrame],
    ):
        await self._propagate(
            StreamFrames(
                chat_id,
                Direction.from_raw(mode),
                Device.from_raw(device),
                [
                    Frame(
                        x.ssrc,
                        x.data,
                        Frame.Info(
                            x.frame_data.absolute_capture_timestamp_ms,
                            x.frame_data.width,
                            x.frame_data.height,
                            x.frame_data.rotation,
                        ),
                    ) for x in frames
                ],
            ),
            self,
        )
