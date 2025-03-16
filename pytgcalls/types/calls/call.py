from enum import auto

from ...types.py_object import PyObject
from ..flag import Flag


class Call(PyObject):
    class Status(Flag):
        ACTIVE = auto()
        PAUSED = auto()
        IDLE = auto()

    class Type(Flag):
        GROUP = auto()
        PRIVATE = auto()

    def __init__(
        self,
        chat_id: int,
        playback: Status,
        capture: Status,
    ):
        self.call_type = Call.Type.GROUP \
            if chat_id < 0 else Call.Type.PRIVATE
        self.playback = playback
        self.capture = capture
