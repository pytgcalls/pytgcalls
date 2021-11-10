from pytgcalls.types.py_object import PyObject


class GroupCall(PyObject):
    def __init__(
            self,
            chat_id: int,
            status: int,
    ):
        self.chat_id: int = chat_id
        self.is_playing: bool = status != 3
        self.status: str = 'unknown'
        if status == 1:
            self.status = 'playing'
        elif status == 2:
            self.status = 'paused'
        elif status == 3:
            self.status = 'not_playing'
