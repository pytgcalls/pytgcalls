from ...types.py_object import PyObject


class GroupCall(PyObject):
    def __init__(
        self,
        chat_id: int,
        binary_status: int,
    ):
        self.chat_id: int = chat_id
        self.is_playing: bool = binary_status != 3
        self.status: str = 'unknown'
        if binary_status == 1:
            self.status = 'playing'
        elif binary_status == 2:
            self.status = 'paused'
        elif binary_status == 3:
            self.status = 'not_playing'
