from ..video_parameters import VideoParameters


class LowQualityVideo(VideoParameters):
    """Low Video Quality (640x360)

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
            640,
            360,
            20,
        )
