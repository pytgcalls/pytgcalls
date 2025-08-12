from typing import Union

from ntgcalls import ConnectionNotFound

from ...exceptions import NoActiveGroupCall
from ...exceptions import NotInCallError
from ...mtproto_required import mtproto_required
from ...mutex import mutex
from ...scaffold import Scaffold
from ...statictypes import statictypes


class LeaveCall(Scaffold):
    @statictypes
    @mtproto_required
    @mutex
    async def leave_call(
        self,
        chat_id: Union[int, str],
    ):
        resolved_chat_id: int = await self.resolve_chat_id(chat_id)
        is_p2p_waiting = (
            resolved_chat_id in self._p2p_configs and
            not self._p2p_configs[resolved_chat_id].wait_data.done()
        )
        if not is_p2p_waiting:
            if resolved_chat_id in self._call_sources:
                sources = self._call_sources[resolved_chat_id]
                for endpoint in list(sources.camera.values()):
                    try:
                        await self._binding.remove_incoming_video(
                            resolved_chat_id,
                            endpoint,
                        )
                    except ConnectionNotFound:
                        pass
                # Remove presentation streams
                for endpoint in list(sources.presentation.values()):
                    try:
                        await self._binding.remove_incoming_video(
                            resolved_chat_id,
                            endpoint,
                        )
                    except ConnectionNotFound:
                        pass
                self._call_sources.pop(resolved_chat_id, None)
            if resolved_chat_id in self._presentations:
                try:
                    await self._binding.stop_presentation(resolved_chat_id)
                except ConnectionNotFound:
                    pass
            try:
                await self._binding.stop(resolved_chat_id)
            except ConnectionNotFound:
                raise NotInCallError()
        if resolved_chat_id < 0:  # type: ignore
            chat_call = await self._app.get_full_chat(
                resolved_chat_id,
            )

            if chat_call is None:
                raise NoActiveGroupCall()

            await self._app.leave_group_call(
                resolved_chat_id,
            )
        else:
            await self._app.discard_call(resolved_chat_id, False)
        if is_p2p_waiting:
            self._p2p_configs.pop(resolved_chat_id)
            return
        if resolved_chat_id < 0:  # type: ignore
            self._need_unmute.discard(resolved_chat_id)
            self._presentations.discard(resolved_chat_id)
            self._call_sources.pop(resolved_chat_id, None)

            self._clear_cache(resolved_chat_id)
