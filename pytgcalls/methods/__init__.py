from .core import Core
from .custom_api import CustomAPI
from .groups import Groups
from .handler import Handler
from .stream import Stream
from .websocket import WebSocket


class Methods(
    Core,
    CustomAPI,
    Groups,
    Stream,
    Handler,
    WebSocket,
):
    pass
