from .mute_stream import MuteStream
from .pause_stream import PauseStream
from .play import Play
from .record import Record
from .resume_stream import ResumeStream
from .time import Time
from .unmute_stream import UnMuteStream


class StreamMethods(
    MuteStream,
    PauseStream,
    Play,
    Record,
    Time,
    ResumeStream,
    UnMuteStream,
):
    pass
