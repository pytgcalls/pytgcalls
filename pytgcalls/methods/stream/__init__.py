from .change_stream import ChangeStream
from .mute_stream import MuteStream
from .pause_stream import PauseStream
from .play import Play
from .played_time import PlayedTime
from .resume_stream import ResumeStream
from .unmute_stream import UnMuteStream


class StreamMethods(
    ChangeStream,
    MuteStream,
    PauseStream,
    Play,
    PlayedTime,
    ResumeStream,
    UnMuteStream,
):
    pass
