from ...scaffold import Scaffold


class EmitSigData(Scaffold):
    async def _emit_sig_data(self, chat_id: int, data: bytes):
        await self._app.send_signaling(
            chat_id,
            data,
        )
