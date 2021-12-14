from pytgcalls.types.py_object import PyObject


class Update(PyObject):
    """A Raw Update

    Attributes:
        chat_id (``int``):
            Unique identifier of chat.

    Parameters:
        chat_id (``int``):
            Unique identifier of chat.

    """

    def __init__(
        self,
        chat_id: int,
    ):
        self.chat_id = chat_id
