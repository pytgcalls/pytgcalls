from typing import Union

from ntgcalls import ConnectionNotFound

from ...exceptions import NoActiveGroupCall
from ...exceptions import NotInGroupCallError
from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...to_async import ToAsync


class LeaveGroupCall(Scaffold):
    @statictypes
    @mtproto_required
    async def leave_group_call(
        self,
        chat_id: Union[int, str],
    ):
        chat_id = await self._resolve_chat_id(chat_id)
        chat_call = await self._app.get_full_chat(
            chat_id,
        )

        if chat_call is None:
            raise NoActiveGroupCall()

        await self._app.leave_group_call(
            chat_id,
        )

        try:
            await ToAsync(
                self._binding.stop,
                chat_id,
            )
        except ConnectionNotFound:
            raise NotInGroupCallError()

        self._need_unmute.discard(chat_id)
