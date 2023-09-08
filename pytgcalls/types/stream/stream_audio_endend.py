from ...types.update import Update


class StreamAudioEnded(Update):
    def __init__(
        self,
        chat_id: int,
    ):
        super().__init__(chat_id)
