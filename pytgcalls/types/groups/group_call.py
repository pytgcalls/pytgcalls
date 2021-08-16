class GroupCall:
    def __init__(
        self,
        chat_id: int,
        status: int,
    ):
        self.chat_id = chat_id
        self.is_playing = status != 3
        if status == 1:
            self.status = PlayingStream()
        elif status == 2:
            self.status = PausedStream()
        elif status == 3:
            self.status = NotPlayingStream()


class PlayingStream:
    pass


class PausedStream:
    pass


class NotPlayingStream:
    pass
