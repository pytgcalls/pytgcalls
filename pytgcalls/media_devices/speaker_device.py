from .device_info import DeviceInfo


class SpeakerDevice(DeviceInfo):
    def __init__(
        self,
        name: str,
        metadata: str,
    ):
        super().__init__(name, metadata, False)
