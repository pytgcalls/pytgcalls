from enum import auto

from ...types.py_object import PyObject
from ..flag import Flag


class GroupCallMessage(PyObject):
    class Action(Flag):
        RECEIVED = auto()
        DELETED = auto()

    def __init__(
        self,
        message_id: int,
        sender_id: int,
        text: str,
        html: str,
        date: int,
        stars: int,
        from_admin: bool,
    ):
        self.message_id: int = message_id
        self.sender_id: int = sender_id
        self.text: str = text
        self.html: str = html
        self.date: int = date
        self.stars: int = stars
        self.from_admin: bool = from_admin
