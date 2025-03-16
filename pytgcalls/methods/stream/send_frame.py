from typing import Union

from ntgcalls import ConnectionNotFound
from ntgcalls import FrameData

from ...exceptions import NotInCallError
from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...types import Device
from ...types import Frame


class SendFrame(Scaffold):
    @statictypes
    @mtproto_required
    async def send_frame(
        self,
        chat_id: Union[int, str],
        device: Device,
        data: bytes,
        frame_data: Frame.Info = Frame.Info(),
    ):
        chat_id = await self.resolve_chat_id(chat_id)
        try:
            return await self._binding.send_external_frame(
                chat_id,
                Device.to_raw(device),
                data,
                FrameData(
                    frame_data.capture_time,
                    frame_data.rotation,
                    frame_data.width,
                    frame_data.height,
                ),
            )
        except ConnectionNotFound:
            raise NotInCallError()
