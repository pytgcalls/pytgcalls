from pytgcalls.types.py_object import PyObject


class GroupCall(PyObject):
    """Info about a group call

    Attributes:
        chat_id (``int``):
            Unique identifier of chat.
        is_playing (``bool``):
            Check if exist any sort of stream
        status (``str``):
            Status of Stream

    Parameters:
        chat_id (``int``):
            Unique identifier of chat.
        binary_status (``int``):
            PyTgCalls API parameter.
    """

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
