from .change_volume_call import ChangeVolumeCall
from .get_participants import GetParticipants
from .leave_group_call import LeaveGroupCall


class Groups(
    ChangeVolumeCall,
    GetParticipants,
    LeaveGroupCall,
):
    pass
