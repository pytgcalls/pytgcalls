from .device_info import DeviceInfo


class InputDevice(DeviceInfo):
    def __init__(
        self,
        name: str,
        metadata: str,
        is_video: bool,
    ):
        super().__init__(name, metadata, is_video)
