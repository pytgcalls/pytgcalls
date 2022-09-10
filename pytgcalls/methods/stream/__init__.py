from .change_stream import ChangeStream
from .mute_stream import MuteStream
from .pause_stream import PauseStream
from .played_time import PlayedTime
from .resume_stream import ResumeStream
from .unmute_stream import UnMuteStream


class Stream(
    ChangeStream,
    MuteStream,
    PauseStream,
    PlayedTime,
    ResumeStream,
    UnMuteStream,
):
    pass
