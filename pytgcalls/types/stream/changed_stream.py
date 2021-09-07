from ...types.update import Update


class ChangedStream(Update):
    def __init__(
        self,
        chat_id: int,
    ):
        super().__init__(chat_id)

    def __str__(self):
        return 'CHANGED_STREAM'
