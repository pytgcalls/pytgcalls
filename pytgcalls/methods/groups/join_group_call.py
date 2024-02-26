import logging
from typing import Any
from typing import Optional
from typing import Union

from deprecation import deprecated

from ...exceptions import AlreadyJoinedError
from ...mtproto_required import mtproto_required
from ...mutex import mutex
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...types.raw.stream import Stream

py_logger = logging.getLogger('pytgcalls')


class JoinGroupCall(Scaffold):
    @deprecated(
        deprecated_in='1.3.0',
        details='Use PyTgCalls.play() instead.',
    )
    @mutex
    @statictypes
    @mtproto_required
    async def join_group_call(
        self,
        chat_id: Union[int, str],
        stream: Optional[Stream] = None,
        invite_hash: Optional[str] = None,
        join_as: Any = None,
        auto_start: bool = True,
    ):
        chat_id = await self._resolve_chat_id(chat_id)
        if chat_id in self._binding.calls():
            raise AlreadyJoinedError()
        await self.play(
            chat_id,
            stream,
            invite_hash,
            join_as,
            auto_start,
        )
