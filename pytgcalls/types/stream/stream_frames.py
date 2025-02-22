from typing import List

from ...types.update import Update
from .device import Device
from .direction import Direction
from .frame import Frame


class StreamFrames(Update):
    def __init__(
        self,
        chat_id: int,
        direction: Direction,
        device: Device,
        frames: List[Frame],
    ):
        super().__init__(chat_id)
        self.direction = direction
        self.device = device
        self.frames = frames
