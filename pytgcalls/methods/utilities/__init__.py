from .cache_peer import CachePeer
from .get_max_voice_chat import GetMaxVoiceChat
from .ping import Ping
from .pyrogram_handler import PyrogramHandler
from .start import Start


class Utilities(
    CachePeer,
    GetMaxVoiceChat,
    Ping,
    PyrogramHandler,
    Start,
):
    pass
