from ...scaffold import Scaffold


class GetCall(Scaffold):
    def get_call(
        self,
        chat_id: int,
    ):
        return self._call_holder.get_call(
            chat_id,
        )
