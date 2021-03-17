class StreamType:
    def __init__(self):
        self._stream_type = 0


    # This set seconds buffer to max 3 seconds to load in cache
    # But this make cpu consumption more heavy
    @property
    def live_stream(self):
        self._stream_type = 3
        return self

    # This set seconds buffer to max 10 seconds to load in cache
    # But this make not adaptable to live stream or ffmpeg live conversion
    @property
    def local_stream(self):
        self._stream_type = 10
        return self

    @property
    def stream_mode(self):
        return self._stream_type
