import logging
from typing import Optional
from typing import Union

from ntgcalls import FileError
from ntgcalls import StreamMode

from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...types import CallConfig
from ...types import GroupCallConfig
from ...types.raw import Stream
from ..utilities.stream_params import StreamParams

py_logger = logging.getLogger('pytgcalls')


class Record(Scaffold):
    @statictypes
    @mtproto_required
    async def record(
        self,
        chat_id: Union[int, str],
        stream: Optional[Stream] = None,
        config: Optional[Union[CallConfig, GroupCallConfig]] = None,
    ):
        chat_id = await self.resolve_chat_id(chat_id)
        media_description = await StreamParams.get_record_params(
            stream,
        )
        if chat_id not in await self._binding.calls():
            await self.play(chat_id, config=config)
        try:
            return await self._binding.set_stream_sources(
                chat_id,
                StreamMode.PLAYBACK,
                media_description,
            )
        except FileError as e:
            raise FileNotFoundError(e)
