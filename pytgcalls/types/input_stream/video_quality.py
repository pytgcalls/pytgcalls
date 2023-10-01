from enum import Enum


class VideoQuality(Enum):
    UHD_4K = (3840, 2160, 60)
    QHD_2K = (2560, 1440, 60)
    FHD_1080p = (1920, 1080, 60)
    HD_720p = (1280, 720, 30)
    SD_480p = (854, 480, 30)
    SD_360p = (640, 360, 30)
