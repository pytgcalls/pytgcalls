from enum import auto
from enum import Flag

from ...types.py_object import PyObject


class Call(PyObject):
    class Status(Flag):
        PLAYING = auto()
        PAUSED = auto()
        IDLE = auto()

        def __repr__(self):
            cls_name = self.__class__.__name__
            return f'{cls_name}.{self.name}'

    class Type(Flag):
        GROUP = auto()
        PRIVATE = auto()

        def __repr__(self):
            cls_name = self.__class__.__name__
            return f'{cls_name}.{self.name}'

    def __init__(
        self,
        chat_id: int,
        status: Status,
    ):
        self.chat_id: int = chat_id
        self.call_type = Call.Type.GROUP \
            if chat_id < 0 else Call.Type.PRIVATE
        self.status = status
