from typing import Union

from ..types.py_object import PyObject


class Update(PyObject):
    def __init__(
        self,
        chat_id: Union[int, str],
    ):
        self.chat_id = chat_id
