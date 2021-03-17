class StreamType:
    def __init__(self):
        self._stream_type = 0

    @property
    def live_stream(self):
        self._stream_type = 3
        return self

    @property
    def local_stream(self):
        self._stream_type = 10
        return self

    @property
    def stream_mode(self):
        return self._stream_type
