from ...exceptions import NoActiveGroupCall
from ...exceptions import UnsupportedMethod
from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes


class DeleteParticipantMessages(Scaffold):
    @statictypes
    @mtproto_required
    async def delete_participant_messages(
        self,
        chat_id: int | str,
        participant_id: int | str,
        report_spam: bool = False,
    ):
        chat_id = await self.resolve_chat_id(chat_id)
        if chat_id >= 0:  # type: ignore
            raise UnsupportedMethod()
        input_call = await self._app.get_input_call(
            chat_id,
        )
        if input_call is None:
            raise NoActiveGroupCall()
        await self._app.delete_group_call_participant_messages(
            chat_id,
            await self._app.resolve_peer(participant_id),
            report_spam,
        )
