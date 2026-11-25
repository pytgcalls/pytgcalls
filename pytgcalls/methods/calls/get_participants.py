import copy

from ntgcalls import ConnectionError
from ntgcalls import ConnectionNotFound

from ...exceptions import UnsupportedMethod
from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...types.chats import GroupCallParticipant
from ...types.list import List


class GetParticipants(Scaffold):
    @statictypes
    @mtproto_required
    async def get_participants(
        self,
        chat_id: int | str,
    ) -> List[GroupCallParticipant] | None:
        chat_id = await self.resolve_chat_id(chat_id)
        if chat_id >= 0:  # type: ignore
            raise UnsupportedMethod()
        participants = await self._app.get_group_call_participants(
            chat_id,
        )
        try:
            chain_participants = set(
                await self._binding.get_e2e_participants(chat_id),
            )
        except (ConnectionError, ConnectionNotFound):
            return participants
        result = List()
        for participant in participants:
            participant = copy.copy(participant)
            participant.has_e2e_key = participant.user_id in chain_participants
            result.append(participant)
        return result
