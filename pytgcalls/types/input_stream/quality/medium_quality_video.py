from ..video_parameters import VideoParameters


class MediumQualityVideo(VideoParameters):
    def __init__(self):
        super().__init__(
            854,
            480,
            20,
        )
