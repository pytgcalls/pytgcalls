from .change_stream import ChangeStream
from .pause_stream import PauseStream
from .resume_stream import ResumeStream


class Stream(PauseStream, ResumeStream, ChangeStream):
    pass
