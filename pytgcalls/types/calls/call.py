from ntgcalls import StreamStatus

from pytgcalls.types.py_object import PyObject


class Call(PyObject):
    def __init__(
        self,
        chat_id: int,
        status: StreamStatus,
    ):
        self.chat_id: int = chat_id
        self.status: StreamStatus = status
