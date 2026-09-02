from enum import auto

from ntgcalls import SsrcGroup

from ...types.py_object import PyObject
from ..flag import Flag


class GroupCallParticipant(PyObject):
    class Action(Flag):
        JOINED = auto()
        LEFT = auto()
        KICKED = auto()
        UPDATED = auto()

    class SourceInfo(PyObject):
        def __init__(
            self,
            endpoint: str,
            sources: list[SsrcGroup],
        ):
            self.endpoint: str = endpoint
            self.sources: list[SsrcGroup] = sources

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
        source: int,
        video_info: SourceInfo | None,
        presentation_info: SourceInfo | None,
    ):
        self.user_id: int = user_id
        self.muted: bool = muted
        self.muted_by_admin: bool = muted_by_admin
        self.video: bool = video
        self.screen_sharing: bool = screen_sharing
        self.source: int = source
        self.video_camera: bool = video_camera
        self.raised_hand: bool = raised_hand
        self.volume: int = volume
        self.video_info: GroupCallParticipant.SourceInfo | None = video_info
        self.presentation_info: GroupCallParticipant.SourceInfo | None = (
            presentation_info
        )
