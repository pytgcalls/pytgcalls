from ..video_parameters import VideoParameters


class MediumQualityVideo(VideoParameters):
    """Medium Video Quality (854x480)

    Attributes:
        width (``int``):
            Video width
        height (``int``):
            Video height
        frame_rate (``int``):
            Framerate of video
    """

    def __init__(self):
        super().__init__(
            854,
            480,
            20,
        )
