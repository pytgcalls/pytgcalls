from .b_colors import BColors
from .generate_session import GenerateSession
from .get_cache_id import GetCacheId
from .get_cache_peer import GetCachePeer
from .get_max_voice_chat import GetMaxVoiceChat
from .get_port_server import GetPortServer
from .run_js import RunJS
from .spawn_process import SpawnProcess


class Core(
    GenerateSession,
    GetCacheId,
    GetCachePeer,
    GetMaxVoiceChat,
    GetPortServer,
    SpawnProcess,
    BColors,
    RunJS,
):
    pass
