class GroupCall:
    def __init__(
            self,
            chat_id: int,
            status: int,
    ):
        self.chat_id = chat_id
        self.is_playing = status != 3
        self.status: Status = UnknownStatus()
        if status == 1:
            self.status = PlayingStream()
        elif status == 2:
            self.status = PausedStream()
        elif status == 3:
            self.status = NotPlayingStream()


class Status:
    pass


class PlayingStream(Status):
    pass


class PausedStream(Status):
    pass


class NotPlayingStream(Status):
    pass


class UnknownStatus(Status):
    pass
