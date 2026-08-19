from ...scaffold import Scaffold


class EmitSignalingData(Scaffold):
    async def _emit_signaling_data(self, chat_id: int, data: bytes):
        await self._app.send_signaling(
            chat_id,
            data,
        )
