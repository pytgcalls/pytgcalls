from .api_backend import ApiBackend
from .change_volume_voice_call import ChangeVolumeVoiceCall
from .event_finish import EventFinish
from .get_partecipants import GetPartecipants
from .join_voice_call import JoinVoiceCall
from .leave_voice_call import LeaveVoiceCall
from .load_full_chat import LoadFullChat
from .start_web_app import StartWebApp
from .update_call_data import UpdateCallData


class WebSocket(
    ApiBackend,
    ChangeVolumeVoiceCall,
    EventFinish,
    GetPartecipants,
    JoinVoiceCall,
    LeaveVoiceCall,
    LoadFullChat,
    StartWebApp,
    UpdateCallData,
):
    pass
