from typing import Optional
from typing import Union

from ntgcalls import ConnectionNotFound
from ntgcalls import FileError

from ...exceptions import NotInGroupCallError
from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...to_async import ToAsync
from ...types.raw.stream import Stream
from ..utilities.stream_params import StreamParams


class ChangeStream(Scaffold):
    @statictypes
    @mtproto_required
    async def change_stream(
        self,
        chat_id: Union[int, str],
        stream: Optional[Stream] = None,
    ):
        chat_id = await self._resolve_chat_id(chat_id)
        try:
            await ToAsync(
                self._binding.change_stream,
                chat_id,
                await StreamParams.get_stream_params(stream),
            )
        except FileError as e:
            raise FileNotFoundError(e)
        except ConnectionNotFound:
            raise NotInGroupCallError()
