from ...types.update import Update


class ErrorDuringJoin(Update):
    def __init__(
        self,
        chat_id: int,
    ):
        super().__init__(chat_id)

    def __str__(self):
        return 'JOIN_ERROR'
