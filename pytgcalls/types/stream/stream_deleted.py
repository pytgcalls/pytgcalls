from ...types.update import Update

# TODO deprecation warning


class StreamDeleted(Update):

    def __init__(
        self,
        chat_id: int,
    ):
        super().__init__(chat_id)
