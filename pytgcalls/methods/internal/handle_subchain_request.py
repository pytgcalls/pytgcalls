from ntgcalls import SubchainRequest

from pytgcalls.scaffold import Scaffold


class HandleSubchainRequest(Scaffold):
    async def _handle_subchain_request(
        self,
        chat_id: int,
        subchain_request: SubchainRequest
    ):
        result = await self._app.get_subchain_blocks(
            chat_id,
            subchain_request
        )
        if result:
            await self._binding.apply_blocks(
                chat_id,
                result.sub_chain_id,
                result.next_offset,
                result.blocks,
                True,
            )
        await self._binding.finish_subchain_request(
            chat_id,
            subchain_request.subchain,
        )