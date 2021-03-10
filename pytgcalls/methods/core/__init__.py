from .b_colors import BColors
from .generate_session import GenerateSession
from .get_port_server import GetPortServer
from .get_user_id import GetUserId
from .run_js import RunJS
from .spawn_process import SpawnProcess


class Core(
    GenerateSession,
    GetUserId,
    GetPortServer,
    SpawnProcess,
    BColors,
    RunJS,
):
    pass
