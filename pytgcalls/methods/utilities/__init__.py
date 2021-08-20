from .cache_peer import CachePeer
from .get_max_voice_chat import GetMaxVoiceChat
from .is_connected import IsConnected
from .ping import Ping
from .pyrogram_handler import PyrogramHandler
from .start import Start


class Utilities(
    CachePeer,
    GetMaxVoiceChat,
    IsConnected,
    Ping,
    PyrogramHandler,
    Start,
):
    pass
