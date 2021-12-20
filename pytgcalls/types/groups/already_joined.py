from ...types.update import Update


class AlreadyJoined(Update):
    def __init__(
        self,
        chat_id: int,
    ):
        super().__init__(chat_id)
