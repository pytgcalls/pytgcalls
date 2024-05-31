from enum import auto

from ...types.py_object import PyObject
from ..flag import Flag


class GroupCallParticipant(PyObject):
    class Action(Flag):
        JOINED = auto()
        LEFT = auto()
        UPDATED = auto()

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
        joined: bool,
        left: bool,
    ):
        self.user_id: int = user_id
        self.muted: bool = muted
        self.muted_by_admin: bool = muted_by_admin
        self.video: bool = video
        self.screen_sharing: bool = screen_sharing
        self.video_camera: bool = video_camera
        self.raised_hand: bool = raised_hand
        self.volume: int = volume
        if joined:
            self.action = self.Action.JOINED
        elif left:
            self.action = self.Action.LEFT
        else:
            self.action = self.Action.UPDATED
