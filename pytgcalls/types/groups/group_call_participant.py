from pytgcalls.types.py_object import PyObject


class GroupCallParticipant(PyObject):
    """Info about a group call participant

    Attributes:
        user_id (``int``):
            Unique identifier of participant.
        muted (``bool``):
            Whether the participant is muted
        muted_by_admin (``bool``):
            Whether the participant is muted by
            admin
        video (``bool``):
            Whether this participant is currently
            broadcasting a video stream
        screen_sharing (``bool``):
            Whether this participant is currently
            broadcasting a screen sharing
        video_camera (``bool``):
            Whether this participant is currently
            broadcasting a video camera
        raised_hand (``bool``):
            Whether this participant have
            raised the hand
        volume (``int``):
            Volume level of the participant

    Parameters:
        user_id (``int``):
            Unique identifier of participant.
        muted (``bool``):
            Telegram API parameter.
        muted_by_admin (``bool``):
            Telegram API parameter.
        video (``bool``):
            Telegram API parameter.
        screen_sharing (``bool``):
            Telegram API parameter.
        video_camera (``bool``):
            Telegram API parameter.
        raised_hand (``bool``):
            Telegram API parameter.
        volume (``int``):
            Telegram API parameter.
    """

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
