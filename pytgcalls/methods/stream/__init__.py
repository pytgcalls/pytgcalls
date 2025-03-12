from .mute import Mute
from .pause import Pause
from .play import Play
from .record import Record
from .resume import Resume
from .send_frame import SendFrame
from .time import Time
from .unmute import UnMute


class StreamMethods(
    Mute,
    Pause,
    Play,
    Record,
    SendFrame,
    Time,
    Resume,
    UnMute,
):
    pass
