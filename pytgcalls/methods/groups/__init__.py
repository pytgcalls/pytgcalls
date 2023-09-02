from .active_calls import ActiveCalls
from .calls import Calls
from .change_volume_call import ChangeVolumeCall
from .get_active_call import GetActiveCall
from .get_call import GetCall
from .get_participants import GetParticipants
from .join_group_call import JoinGroupCall
from .leave_group_call import LeaveGroupCall


class Groups(
    ActiveCalls,
    Calls,
    ChangeVolumeCall,
    GetActiveCall,
    GetCall,
    GetParticipants,
    JoinGroupCall,
    LeaveGroupCall,
):
    pass
