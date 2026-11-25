import logging

from ntgcalls import CallType
from ntgcalls import ConnectionNotFound

from ...scaffold import Scaffold
from ...types.calls import CallSources

py_logger = logging.getLogger('pytgcalls')


class RejoinCall(Scaffold):
    async def _rejoin_call(self, chat_id: int):
        async with await self._chat_lock.acquire(chat_id):
            try:
                call_type = await self._binding.get_call_type(chat_id)
            except ConnectionNotFound:
                self._reconnecting.discard(chat_id)
                return
            if call_type not in (CallType.GROUP, CallType.CONFERENCE):
                self._reconnecting.discard(chat_id)
                return
            py_logger.debug(f'Rejoining the call in {chat_id}')
            presenting = chat_id in self._presentations
            self._presentations.discard(chat_id)
            # noinspection PyBroadException
            try:
                self._wait_connect[chat_id] = self.loop.create_future()
                state = await self._binding.get_state(chat_id)
                if call_type == CallType.CONFERENCE:
                    conference_params = await self._binding.rejoin_conference(
                        chat_id,
                        await self._app.get_conference_last_block(chat_id),
                    )
                    result_params = await self._app.join_group_call(
                        chat_id,
                        conference_params.payload,
                        state.video_stopped,
                        self._cache_user_peer.get(chat_id),
                        None,
                        conference_params.block,
                        int.from_bytes(
                            conference_params.public_key,
                            'little',
                            signed=True,
                        ),
                    )
                else:
                    result_params = await self._app.join_group_call(
                        chat_id,
                        await self._binding.rejoin(chat_id),
                        state.video_stopped,
                        self._cache_user_peer.get(chat_id),
                        self._invite_hashes.get(chat_id),
                    )
                await self._binding.connect(
                    chat_id,
                    result_params,
                    False,
                )
                await self._wait_connect[chat_id]
                self._wait_connect.pop(chat_id, None)
                self._call_sources[chat_id] = CallSources()
                await self._update_sources(chat_id)
                if presenting:
                    await self._join_presentation(chat_id, True)
            except Exception as e:
                py_logger.debug(f'Rejoin of {chat_id} failed: {e}')
                await self._clear_call(chat_id)
            finally:
                self._reconnecting.discard(chat_id)
                future = self._wait_connect.pop(chat_id, None)
                if future is not None:
                    if future.done():
                        if not future.cancelled():
                            future.exception()
                    else:
                        future.cancel()
