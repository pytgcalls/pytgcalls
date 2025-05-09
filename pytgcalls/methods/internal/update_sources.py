from typing import Union

from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...types.calls import CallSources


class UpdateSources(Scaffold):
    async def _update_sources(
        self,
        chat_id: Union[int, str],
    ):
        participants = await self._app.get_group_call_participants(
            chat_id,
        )
        if chat_id not in self._call_sources:
            self._call_sources[chat_id] = CallSources()
        for x in participants:
            if x.video_info is not None and \
                    x.user_id not in self._call_sources[chat_id].camera:
                self._call_sources[chat_id].camera[
                    x.user_id
                ] = x.video_info.endpoint
                await self._binding.add_incoming_video(
                    chat_id,
                    x.video_info.endpoint,
                    x.video_info.sources,
                )
            if x.presentation_info is not None and \
                    x.user_id not in self._call_sources[chat_id].presentation:
                self._call_sources[chat_id].presentation[
                    x.user_id
                ] = x.presentation_info.endpoint
                await self._binding.add_incoming_video(
                    chat_id,
                    x.presentation_info.endpoint,
                    x.presentation_info.sources,
                )
            if x.user_id == BridgedClient.chat_id(
                self._cache_local_peer,
            ) and x.muted_by_admin:
                self._need_unmute.add(chat_id)
