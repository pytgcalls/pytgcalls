class StreamType:
    """StreamType, the main means for setting
    the streaming mode.

    Attributes:
        live_stream (``self``):
            Streaming mode for Live Video, or HTTP online video
        local_stream (``self``):
            Streaming mode for Downloaded Video
        pulse_stream (``self``):
            Streaming mode for Live Video, HTTP online video,
            or Local Video
        stream_mode (``int``):
            Get the int value of stream mode
    """

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
