from pyrogram.raw.functions.phone import EditGroupCallParticipant

from ...exceptions import NoActiveGroupCall
from ...exceptions import NodeJSNotRunning
from ...exceptions import PyrogramNotSet
from ...scaffold import Scaffold


class ChangeVolumeCall(Scaffold):
    async def change_volume_call(self, chat_id: int, volume: int):
        if self._app is not None:
            if self._wait_until_run is not None:
                if not self._wait_until_run.done():
                    await self._wait_until_run
                chat_call = await self._full_chat_cache.get_full_chat(
                    chat_id,
                )
                if chat_call is not None:
                    await self._app.send(
                        EditGroupCallParticipant(
                            call=chat_call,
                            participant=self._cache_user_peer.get(chat_id),
                            muted=False,
                            volume=volume * 100,
                        ),
                    )
                else:
                    raise NoActiveGroupCall()
            else:
                raise NodeJSNotRunning()
        else:
            raise PyrogramNotSet()
