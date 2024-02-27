from ..types.py_object import PyObject


class Update(PyObject):
    def __init__(
        self,
        chat_id: int,
    ):
        self.chat_id = chat_id
