from .raw_update_handler import RawUpdateHandler
from .stream_ended_handler import StreamEndedHandler


class Handlers(
    RawUpdateHandler,
    StreamEndedHandler,
):
    pass
