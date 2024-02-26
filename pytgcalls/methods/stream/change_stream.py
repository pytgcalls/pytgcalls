from typing import Optional
from typing import Union

from deprecation import deprecated

from ...exceptions import NotInGroupCallError
from ...mtproto_required import mtproto_required
from ...mutex import mutex
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...types.raw.stream import Stream


class ChangeStream(Scaffold):
    @deprecated(
        deprecated_in='1.3.0',
        details='Use PyTgCalls.play() instead.',
    )
    @mutex
    @statictypes
    @mtproto_required
    async def change_stream(
        self,
        chat_id: Union[int, str],
        stream: Optional[Stream] = None,
    ):
        chat_id = await self._resolve_chat_id(chat_id)
        if chat_id not in self._binding.calls():
            raise NotInGroupCallError()

        await self.play(chat_id, stream)
