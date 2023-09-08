from typing import Union

from ntgcalls import ConnectionError

from ...exceptions import NoActiveGroupCall
from ...exceptions import NoMtProtoClientSet
from ...exceptions import NotInGroupCallError
from ...mtproto import BridgedClient
from ...scaffold import Scaffold
from ...to_async import ToAsync
from ...types import LeftVoiceChat


class LeaveGroupCall(Scaffold):
    async def leave_group_call(
        self,
        chat_id: Union[int, str],
    ):
        if self._app is not None:
            try:
                chat_id = int(chat_id)
            except ValueError:
                chat_id = BridgedClient.chat_id(
                    await self._app.resolve_peer(chat_id),
                )

            chat_call = await self._app.get_full_chat(
                chat_id,
            )

            if chat_call is not None:
                await self._app.leave_group_call(
                    chat_id,
                )

                try:
                    await ToAsync(
                        self._binding.stop,
                        chat_id,
                    )
                except ConnectionError:
                    raise NotInGroupCallError()

                await self._on_event_update.propagate(
                    'RAW_UPDATE_HANDLER',
                    self,
                    LeftVoiceChat(chat_id),
                )
            else:
                raise NoActiveGroupCall()
        else:
            raise NoMtProtoClientSet()
