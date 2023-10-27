from .change_volume_call import ChangeVolumeCall
from .get_participants import GetParticipants
from .join_group_call import JoinGroupCall
from .leave_group_call import LeaveGroupCall


class Groups(
    ChangeVolumeCall,
    GetParticipants,
    JoinGroupCall,
    LeaveGroupCall,
):
    pass
