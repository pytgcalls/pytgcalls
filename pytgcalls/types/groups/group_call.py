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
    def __str__(self):
        return 'playing'


class PausedStream(Status):
    def __str__(self):
        return 'paused'


class NotPlayingStream(Status):
    def __str__(self):
        return 'not_playing'


class UnknownStatus(Status):
    def __str__(self):
        return 'unknown'
