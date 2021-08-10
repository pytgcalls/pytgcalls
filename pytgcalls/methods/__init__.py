from .async_request import AsyncRequest
from .call_property import CallProperty
from .core import Core
from .groups import Groups
from .handler import Handler
from .stream import Stream
from .websocket import WebSocket


class Methods(
    AsyncRequest,
    CallProperty,
    Core,
    Groups,
    Stream,
    Handler,
    WebSocket,
):
    pass
