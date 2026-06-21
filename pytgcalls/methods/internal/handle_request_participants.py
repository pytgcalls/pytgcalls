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

        audio_ssrc_mapping: List[SsrcMapping] = []
        for participant in participants:
            audio_ssrc_mapping.append(
                SsrcMapping(
                    participant.user_id,
                    participant.source,
                ),
            )
        await self._binding.update_audio_ssrc_mappings(
            chat_id,
            audio_ssrc_mapping,
        )
