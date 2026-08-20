from typing import Dict
from typing import List

from ntgcalls import SsrcMapping

from pytgcalls.scaffold import Scaffold


class HandleRequestParticipants(Scaffold):
    async def _handle_request_participants(
        self,
        chat_id: int,
    ):
        participants = await self._app.get_group_call_participants(
            chat_id,
        )

        audio_sources: Dict[int, int] = {
            participant.user_id: participant.source
            for participant in participants
        }
        call_sources = self._call_sources.get(chat_id)
        if call_sources is not None:
            if call_sources.audio == audio_sources:
                return
            call_sources.audio = audio_sources

        audio_ssrc_mapping: List[SsrcMapping] = []
        for user_id, source in audio_sources.items():
            audio_ssrc_mapping.append(
                SsrcMapping(
                    user_id,
                    source,
                ),
            )
        await self._binding.update_audio_ssrc_mappings(
            chat_id,
            audio_ssrc_mapping,
        )
