from .core import Core
from .custom_api import CustomAPI
from .groups import Groups
from .stream import Stream
from .handler import Handler
from .websocket import WebSocket


class Methods(
    Core,
    CustomAPI,
    Groups,
    Stream,
    Handler,
    WebSocket
):
    pass
