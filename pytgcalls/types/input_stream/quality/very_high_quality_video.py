from ..video_parameters import VideoParameters


class VeryHighQualityVideo(VideoParameters):
    def __init__(self):
        super().__init__(
            1920,
            1080,
            60,
        )
