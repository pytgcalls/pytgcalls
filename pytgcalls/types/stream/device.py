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

    @staticmethod
    def to_raw(device: 'Device'):
        if device == Device.MICROPHONE:
            return StreamDevice.MICROPHONE
        if device == Device.SPEAKER:
            return StreamDevice.SPEAKER
        if device == Device.CAMERA:
            return StreamDevice.CAMERA
        if device == Device.SCREEN:
            return StreamDevice.SCREEN
        return None
