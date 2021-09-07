from ...types import Update


class StreamVideoEnded(Update):
    def __init__(
        self,
        chat_id: int,
    ):
        super().__init__(chat_id)

    def __str__(self):
        return 'STREAM_VIDEO_ENDED'
