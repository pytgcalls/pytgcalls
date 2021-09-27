from pytgcalls.types.py_object import PyObject


class GroupCallParticipant(PyObject):
    def __init__(
        self,
        user_id: int,
        muted: bool,
        muted_by_admin: bool,
        have_video: bool,
        raised_hand: bool,
        volume: int,
    ):
        self.user_id: int = user_id
        self.muted: bool = muted
        self.muted_by_admin: bool = muted_by_admin
        self.have_video: bool = have_video
        self.raised_hand: bool = raised_hand
        self.volume = volume
