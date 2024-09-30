from .mute_stream import MuteStream
from .pause_stream import PauseStream
from .play import Play
from .resume_stream import ResumeStream
from .time import Time
from .unmute_stream import UnMuteStream


class StreamMethods(
    MuteStream,
    PauseStream,
    Play,
    Time,
    ResumeStream,
    UnMuteStream,
):
    pass
