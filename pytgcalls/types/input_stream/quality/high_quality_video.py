from ..video_parameters import VideoParameters


class HighQualityVideo(VideoParameters):
    def __init__(self):
        super().__init__(
            1280,
            720,
            20,
        )
