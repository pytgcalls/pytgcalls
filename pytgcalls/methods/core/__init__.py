from .generate_session import GenerateSession
from .get_user_id import GetUserId
from .get_port_server import GetPortServer
from .get_active_voice_chat import GetActiveVoiceChat
from .spawn_process import SpawnProcess
from .b_colors import BColors
from .run_js import RunJS


class Core(
    GenerateSession,
    GetUserId,
    GetPortServer,
    GetActiveVoiceChat,
    SpawnProcess,
    BColors,
    RunJS
):
    pass
