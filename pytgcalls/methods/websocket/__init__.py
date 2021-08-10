from .api_backend import ApiBackend
from .change_volume_voice_call import ChangeVolumeVoiceCall
from .event_finish import EventFinish
from .get_participants import GetParticipants
from .join_voice_call import JoinVoiceCall
from .leave_voice_call import LeaveVoiceCall
from .load_chat_call import LoadChatCall
from .multi_instance_manager import MultiInstanceManager
from .start_web_app import StartWebApp
from .update_call_data import UpdateCallData


class WebSocket(
    ApiBackend,
    ChangeVolumeVoiceCall,
    EventFinish,
    GetParticipants,
    JoinVoiceCall,
    LeaveVoiceCall,
    LoadChatCall,
    MultiInstanceManager,
    StartWebApp,
    UpdateCallData,
):
    pass
