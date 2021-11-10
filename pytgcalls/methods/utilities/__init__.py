from .cache_peer import CachePeer
from .get_max_voice_chat import GetMaxVoiceChat
from .is_connected import IsConnected
from .mtproto_handler import MtProtoHandler
from .ping import Ping
from .run import Run
from .start import Start


class Utilities(
    CachePeer,
    GetMaxVoiceChat,
    IsConnected,
    Ping,
    MtProtoHandler,
    Run,
    Start,
):
    pass
