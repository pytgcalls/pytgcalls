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

    """
    *** Pulse Stream ***
    Send bytes like a pulsation, and this reduce the slice,
    because the slice is too heavy

    Support: LiveStream, LocalStream
    """
    @property
    def pulse_stream(self):
        self._stream_type = 4
        return self

    @property
    def stream_mode(self):
        return self._stream_type
