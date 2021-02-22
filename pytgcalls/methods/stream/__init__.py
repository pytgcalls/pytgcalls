from .pause_stream import PauseStream
from .resume_stream import ResumeStream
from .change_stream import ChangeStream


class Stream(PauseStream, ResumeStream, ChangeStream):
    pass
