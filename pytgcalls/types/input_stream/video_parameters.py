class VideoParameters:
    def __init__(
        self,
        width: int = 640,
        height: int = 360,
        frame_rate: int = 25,
    ):
        self.width: int = width
        self.height: int = height
        self.frame_rate: int = frame_rate
