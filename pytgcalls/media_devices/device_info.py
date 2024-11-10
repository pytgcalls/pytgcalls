class DeviceInfo:
    def __init__(
        self,
        name: str,
        metadata: str,
        is_video: bool,
    ):
        self.title = name
        self.metadata = metadata
        self.is_video = is_video

    def __repr__(self):
        return self.title
