from ..video_parameters import VideoParameters


class HighQualityVideo(VideoParameters):
    """High Video Quality (1280x720)

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
            1280,
            720,
            20,
        )
