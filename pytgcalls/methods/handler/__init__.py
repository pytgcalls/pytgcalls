from .on_event_update import OnEventUpdate
from .on_stream_end import OnStreamEnd


class Handler(OnEventUpdate, OnStreamEnd):
    pass
