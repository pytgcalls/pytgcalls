from .b_colors import BColors
from .generate_session import GenerateSession
from .get_cache_id import GetCacheId
from .get_cache_peer import GetCachePeer
from .get_max_voice_chat import GetMaxVoiceChat
from .get_port_server import GetPortServer
from .is_running_js_core import IsRunningJsCore
from .run_js import RunJS
from .run_waiting_requests import RunWaitingRequests
from .spawn_process import SpawnProcess


class Core(
    BColors,
    GenerateSession,
    GetCacheId,
    GetCachePeer,
    GetMaxVoiceChat,
    GetPortServer,
    IsRunningJsCore,
    RunJS,
    RunWaitingRequests,
    SpawnProcess,
):
    pass
