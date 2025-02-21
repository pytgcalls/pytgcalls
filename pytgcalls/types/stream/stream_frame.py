from ...types.update import Update
from .device import Device
from .direction import Direction


class StreamFrame(Update):

    class Info:
        def __init__(
            self,
            capture_time: int = 0,
            width: int = 0,
            height: int = 0,
            rotation: int = 0,
        ):
            self.capture_time = capture_time
            self.width = width
            self.height = height
            self.rotation = rotation

    def __init__(
        self,
        chat_id: int,
        ssrc: int,
        direction: Direction,
        device: Device,
        frame: bytes,
        info: Info,
    ):
        super().__init__(chat_id)
        self.ssrc = ssrc
        self.direction = direction
        self.device = device
        self.frame = frame
        self.info = info
