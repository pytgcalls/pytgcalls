from ..video_parameters import VideoParameters


class LowQualityVideo(VideoParameters):

    def __init__(self):
        super().__init__(
            640,
            360,
            20,
        )
