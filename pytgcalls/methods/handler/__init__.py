from .on_event_update import OnEventUpdate
from .on_group_call_invite import OnGroupCallInvite
from .on_stream_end import OnStreamEnd


class Handler(OnEventUpdate, OnGroupCallInvite, OnStreamEnd):
    pass
