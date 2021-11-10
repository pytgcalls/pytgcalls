from .on_closed_voice_chat import OnClosedVoiceChat
from .on_group_call_invite import OnGroupCallInvite
from .on_kicked import OnKicked
from .on_left import OnLeft
from .on_participants_change import OnParticipantsChange
from .on_raw_update import OnRawUpdate
from .on_stream_end import OnStreamEnd


class Decorators(
    OnClosedVoiceChat,
    OnGroupCallInvite,
    OnKicked,
    OnLeft,
    OnParticipantsChange,
    OnRawUpdate,
    OnStreamEnd,
):
    pass
