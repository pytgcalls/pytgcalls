from ...exceptions import NoActiveGroupCall
from ...exceptions import NodeJSNotRunning
from ...exceptions import NoMtProtoClientSet
from ...scaffold import Scaffold


class ChangeVolumeCall(Scaffold):
    async def change_volume_call(self, chat_id: int, volume: int):
        if self._app is not None:
            if self._wait_until_run is not None:
                if not self._wait_until_run.done():
                    await self._wait_until_run
                chat_call = await self._app.get_full_chat(
                    chat_id,
                )
                if chat_call is not None:
                    await self._app.change_volume(
                        chat_id,
                        volume,
                        self._cache_user_peer.get(chat_id),
                    )
                else:
                    raise NoActiveGroupCall()
            else:
                raise NodeJSNotRunning()
        else:
            raise NoMtProtoClientSet()
