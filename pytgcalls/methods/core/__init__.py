from .binding_runner import BindingRunner
from .join_voice_call import JoinVoiceCall
from .leave_voice_call import LeaveVoiceCall


class Core(
    BindingRunner,
    JoinVoiceCall,
    LeaveVoiceCall,
):
    pass
