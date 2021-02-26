from .change_stream import ChangeStream
from .is_playing import IsPlaying
from .pause_stream import PauseStream
from .resume_stream import ResumeStream


class Stream(ChangeStream, IsPlaying, PauseStream, ResumeStream):
    pass
