from enum import Enum


class AudioQuality(Enum):
    STUDIO = (96000, 2)
    HIGH = (48000, 2)
    MEDIUM = (36000, 1)
    LOW = (24000, 1)
