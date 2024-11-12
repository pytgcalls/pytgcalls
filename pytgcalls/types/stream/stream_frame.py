from ...types.update import Update
from .device import Device
from .direction import Direction


class StreamFrame(Update):

    class Info:
        def __init__(
            self,
            capture_time: int,
            width: int,
            height: int,
            rotation: int,
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
