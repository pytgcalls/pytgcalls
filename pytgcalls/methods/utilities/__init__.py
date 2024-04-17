from .cache_peer import CachePeer
from .call_holder import CallHolder
from .cpu_usage import CpuUsage
from .ping import Ping
from .resolve_chat_id import ResolveChatID
from .run import Run
from .start import Start


class Utilities(
    CachePeer,
    CallHolder,
    CpuUsage,
    Ping,
    ResolveChatID,
    Run,
    Start,
):
    pass
