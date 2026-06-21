from pytgcalls.scaffold import Scaffold


class JoinConference(Scaffold):
    async def _join_conference(
        self,
        chat_id
    ):
        last_block = await self._app.get_conference_last_block(
            chat_id,
        )
        conference_params = await self._binding.init_conference(
            chat_id,
            self._my_id,
            last_block,
        )
        public_key = int.from_bytes(
            conference_params.public_key,
            'little',
            signed=True,
        )
        self._cache_user_peer.put(
            chat_id,
            self._cache_local_peer,
        )
        result_params = await self._app.join_group_call(
            chat_id,
            conference_params.payload,
            False,
            self._cache_user_peer.get(chat_id),
            None,
            conference_params.block,
            public_key,
        )
        await self._binding.connect(
            chat_id,
            result_params,
            False,
        )