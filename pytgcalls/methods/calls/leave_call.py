from typing import Union

from ntgcalls import ConnectionNotFound

from ...exceptions import NoActiveGroupCall
from ...exceptions import NotInCallError
from ...mtproto_required import mtproto_required
from ...mutex import mutex
from ...scaffold import Scaffold
from ...statictypes import statictypes


class LeaveCall(Scaffold):
    @mutex
    @statictypes
    @mtproto_required
    async def leave_call(
        self,
        chat_id: Union[int, str],
    ):
        chat_id = await self.resolve_chat_id(chat_id)
        is_p2p_waiting = (
            chat_id in self._p2p_configs and
            not self._p2p_configs[chat_id].wait_data.done()
        )
        if not is_p2p_waiting:
            try:
                await self._binding.stop(chat_id)
            except ConnectionNotFound:
                raise NotInCallError()
        if chat_id < 0:  # type: ignore
            chat_call = await self._app.get_full_chat(
                chat_id,
            )

            if chat_call is None:
                raise NoActiveGroupCall()

            await self._app.leave_group_call(
                chat_id,
            )
        else:
            await self._app.discard_call(chat_id, False)
        if is_p2p_waiting:
            self._p2p_configs.pop(chat_id)
            return
        if chat_id < 0:  # type: ignore
            self._need_unmute.discard(chat_id)
