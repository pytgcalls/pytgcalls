import copy
import logging

from ntgcalls import ConnectionError
from ntgcalls import ConnectionNotFound
from ntgcalls import CryptoError

from ...scaffold import Scaffold
from ...types import GroupCallParticipant
from ...types import UpdatedGroupCallParticipant

py_logger = logging.getLogger('pytgcalls')


class HandleE2EParticipants(Scaffold):
    async def _handle_e2e_participants(
        self,
        chat_id: int,
        participants: list[int] | None = None,
    ):
        if participants is None:
            try:
                participants = await self._binding.get_e2e_participants(
                    chat_id,
                )
            except (ConnectionError, ConnectionNotFound):
                return
        chain_participants = set(participants)
        previous = self._e2e_participants.get(chat_id)
        self._e2e_participants[chat_id] = chain_participants
        if not chain_participants:
            return
        call_participants = await self._app.get_group_call_participants(
            chat_id,
        )
        if previous is not None:
            for participant in call_participants:
                has_e2e_key = participant.user_id in chain_participants
                if has_e2e_key == (participant.user_id in previous):
                    continue
                participant = copy.copy(participant)
                participant.has_e2e_key = has_e2e_key
                await self._propagate(
                    UpdatedGroupCallParticipant(
                        chat_id,
                        GroupCallParticipant.Action.UPDATED,
                        participant,
                    ),
                    self,
                )
        present = {participant.user_id for participant in call_participants}
        present.add(self._my_id)
        stale = list(chain_participants - present)
        if not stale:
            return
        # noinspection PyBroadException
        try:
            block = await self._binding.create_remove_block(chat_id, stale)
            await self._app.delete_conference_call_participants(
                chat_id,
                stale,
                bytes(block),
                True,
            )
        except (ConnectionNotFound, CryptoError):
            pass
        except Exception as e:
            py_logger.debug(f'Removing stale participants failed: {e}')
