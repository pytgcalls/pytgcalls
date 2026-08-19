from ...scaffold import Scaffold


class EmitOutboundBlock(Scaffold):
    async def _emit_outbound_block(self, chat_id: int, block: bytes):
        await self._app.send_conference_call_broadcast(
            chat_id,
            block,
        )
