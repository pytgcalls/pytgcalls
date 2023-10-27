from .cache_peer import CachePeer
from .call_holder import CallHolder
from .get_max_voice_chat import GetMaxVoiceChat
from .mtproto_handler import MTProtoHandler
from .ping import Ping
from .resolve_chat_id import ResolveChatID
from .run import Run
from .start import Start


class Utilities(
    CachePeer,
    CallHolder,
    GetMaxVoiceChat,
    Ping,
    MTProtoHandler,
    ResolveChatID,
    Run,
    Start,
):
    pass
