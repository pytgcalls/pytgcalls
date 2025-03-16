from ntgcalls import DeviceInfo as RawDeviceInfo
from ntgcalls import NTgCalls

from ..types.list import List
from .input_device import InputDevice
from .screen_device import ScreenDevice
from .speaker_device import SpeakerDevice


class MediaDevices:
    @staticmethod
    def _parse_devices(devices: list[RawDeviceInfo], is_video: bool) -> List:
        return List(
            InputDevice(device.name, device.metadata, is_video)
            for device in devices
        )

    @staticmethod
    def microphone_devices() -> List:
        return MediaDevices._parse_devices(
            NTgCalls.get_media_devices().microphone,
            False,
        )

    @staticmethod
    def speaker_devices() -> List:
        return List(
            SpeakerDevice(
                device.name,
                device.metadata,
            )
            for device in NTgCalls.get_media_devices().speaker
        )

    @staticmethod
    def camera_devices() -> List:
        return MediaDevices._parse_devices(
            NTgCalls.get_media_devices().camera,
            True,
        )

    @staticmethod
    def screen_devices() -> List:
        return List(
            ScreenDevice(
                device.name,
                device.metadata,
            )
            for device in NTgCalls.get_media_devices().screen
        )
