from .input_device import InputDevice


class ScreenDevice(InputDevice):
    def __init__(
        self,
        name: str,
        metadata: str,
    ):
        super().__init__(name, metadata, True)
