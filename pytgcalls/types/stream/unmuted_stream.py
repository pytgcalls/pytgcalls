from ...types.update import Update


class UnMutedStream(Update):
    """Raised when unmuted stream successfully

    Attributes:
        chat_id (``int``):
            Unique identifier of chat.

    Parameters:
        chat_id (``int``):
            Unique identifier of chat.
    """

    def __init__(
        self,
        chat_id: int,
    ):
        super().__init__(chat_id)
