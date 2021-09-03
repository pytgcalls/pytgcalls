from .binding_runner import BindingRunner
from .join_voice_call import JoinVoiceCall
from .leave_voice_call import LeaveVoiceCall
from .set_video_call_status import SetVideoCallStatus


class Core(
    BindingRunner,
    JoinVoiceCall,
    LeaveVoiceCall,
    SetVideoCallStatus,
):
    pass
