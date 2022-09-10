class StreamTime:
    """Played time of the stream

    Attributes:
        time (``int``):
            Time of the stream in seconds.

    Parameters:
        time (``int``):
            Time of the stream in seconds.
    """

    def __init__(
        self,
        time: int,
    ):
        self.time = time
