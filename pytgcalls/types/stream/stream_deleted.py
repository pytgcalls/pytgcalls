from ...types.update import Update


class StreamDeleted(Update):
    def __init__(
        self,
        chat_id: int,
    ):
        super().__init__(chat_id)
