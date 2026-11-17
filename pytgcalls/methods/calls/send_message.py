from ...exceptions import NoActiveGroupCall
from ...exceptions import UnsupportedMethod
from ...mtproto_required import mtproto_required
from ...scaffold import Scaffold
from ...statictypes import statictypes
from ...types.chats import GroupCallMessage


class SendMessage(Scaffold):
    @statictypes
    @mtproto_required
    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        stars: int = 0,
    ) -> GroupCallMessage | None:
        chat_id = await self.resolve_chat_id(chat_id)
        input_call = await self._app.get_input_call(
            chat_id,  # type: ignore
        )
        if input_call is None:
            raise NoActiveGroupCall()
        if not text and not stars:
            return None
        message = await self._app.send_group_call_message(
            chat_id,
            text,
            stars,
            self._cache_user_peer.get(chat_id),
        )
        if message is None:
            raise UnsupportedMethod()
        return message
