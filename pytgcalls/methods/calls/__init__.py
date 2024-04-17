from .change_volume_call import ChangeVolumeCall
from .get_participants import GetParticipants
from .leave_call import LeaveCall


class Calls(
    ChangeVolumeCall,
    GetParticipants,
    LeaveCall,
):
    pass
