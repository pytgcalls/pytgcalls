from .on_group_call_invite import OnGroupCallInvite
from .on_kicked import OnKicked
from .on_raw_event import OnRawUpdate
from .on_stream_end import OnStreamEnd


class Handler(OnGroupCallInvite, OnKicked, OnRawUpdate, OnStreamEnd):
    pass
