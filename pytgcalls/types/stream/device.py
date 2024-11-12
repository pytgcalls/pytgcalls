from enum import auto

from ntgcalls import StreamDevice

from ..flag import Flag


class Device(Flag):
    MICROPHONE = auto()
    SPEAKER = auto()
    CAMERA = auto()
    SCREEN = auto()

    @staticmethod
    def from_raw(device: StreamDevice):
        if device == StreamDevice.MICROPHONE:
            return Device.MICROPHONE
        if device == StreamDevice.SPEAKER:
            return Device.SPEAKER
        if device == StreamDevice.CAMERA:
            return Device.CAMERA
        if device == StreamDevice.SCREEN:
            return Device.SCREEN
        return None
