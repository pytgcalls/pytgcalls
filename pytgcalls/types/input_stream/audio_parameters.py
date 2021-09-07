class AudioParameters:
    def __init__(
        self,
        bitrate: int = 48000,
    ):
        self.bitrate: int = 48000 if bitrate > 48000 else bitrate
