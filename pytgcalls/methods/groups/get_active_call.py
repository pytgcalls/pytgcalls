from ...scaffold import Scaffold


class GetActiveCall(Scaffold):
    def get_active_call(
        self,
        chat_id: int,
    ):
        return self._call_holder.get_active_call(
            chat_id,
        )
