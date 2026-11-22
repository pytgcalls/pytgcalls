from enum import Enum


class AudioQuality(Enum):
    MASTER = (96000, 2, 510000)
    STUDIO = (96000, 2, 192000)
    HIGH = (48000, 2, 128000)
    MEDIUM = (36000, 1)
    LOW = (24000, 1)
    VOICE = (48000, 1)
