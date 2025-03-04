from .cache_peer import CachePeer
from .call_holder import CallHolder
from .cpu_usage import CpuUsage
from .join_presentation import JoinPresentation
from .log_retries import LogRetries
from .ping import Ping
from .resolve_chat_id import ResolveChatID
from .run import Run
from .start import Start
from .update_sources import UpdateSources


class Utilities(
    CachePeer,
    CallHolder,
    CpuUsage,
    JoinPresentation,
    LogRetries,
    Ping,
    ResolveChatID,
    Run,
    Start,
    UpdateSources,
):
    pass
