from typing import Union

from ntgcalls import ConnectionError

from ...exceptions import ClientNotStarted
from ...exceptions import NoActiveGroupCall
from ...exceptions import NoMTProtoClientSet
from ...exceptions import NotInGroupCallError
from ...scaffold import Scaffold
from ...to_async import ToAsync
from ...types import LeftVoiceChat

class LeaveGroupCall(Scaffold):
    async def leave_group_call(
        self,
        chat_id: Union[int, str],
    ):
        """
        Leave a group call.

        :param chat_id: Chat ID of the group call.
        :raises NoActiveGroupCall: If there is no active group call.
        :raises ClientNotStarted: If the client is not started.
        :raises NoMTProtoClientSet: If no MTProto client is set.
        :raises NotInGroupCallError: If the user is not in the group call.
        """
        if self._app is not None:
            if self._is_running:
                chat_id = await self._resolve_chat_id(chat_id)
                chat_call = await self._app.get_full_chat(chat_id)

                if chat_call is not None:
                    try:
                        # Check if the user is in the group call before attempting to leave
                        await self._app.check_group_call(chat_id)
                    except NotInGroupCallError:
                        raise NotInGroupCallError()

                    await self._app.leave_group_call(chat_id)

                    try:
                        await ToAsync(self._binding.stop, chat_id)
                    except ConnectionError:
                        raise NotInGroupCallError()

                    if chat_id in self._need_unmute:
                        del self._need_unmute[chat_id]

                    await self._on_event_update.propagate(
                        'RAW_UPDATE_HANDLER',
                        self,
                        LeftVoiceChat(chat_id),
                    )
                else:
                    raise NoActiveGroupCall()
            else:
                raise ClientNotStarted()
        else:
            raise NoMTProtoClientSet()
