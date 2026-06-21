from ..update import Update


class UpdatedEmojis(Update):
    def __init__(
        self,
        chat_id: int,
        emojis: str,
    ):
        super().__init__(chat_id)
        self.emojis = emojis
