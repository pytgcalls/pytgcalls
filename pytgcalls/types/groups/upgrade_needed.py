from ...types.update import Update


class UpgradeNeeded(Update):
    def __init__(
        self,
        chat_id: int,
    ):
        super().__init__(chat_id)
