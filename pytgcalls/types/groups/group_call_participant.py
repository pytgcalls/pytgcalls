from ...types.py_object import PyObject


class GroupCallParticipant(PyObject):
    def __init__(
        self,
        user_id: int,
        muted: bool,
        muted_by_admin: bool,
        video: bool,
        screen_sharing: bool,
        video_camera: bool,
        raised_hand: bool,
        volume: int,
    ):
        self.user_id: int = user_id
        self.muted: bool = muted
        self.muted_by_admin: bool = muted_by_admin
        self.video: bool = video
        self.screen_sharing: bool = screen_sharing
        self.video_camera: bool = video_camera
        self.raised_hand: bool = raised_hand
        self.volume: int = volume
