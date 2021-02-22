from .change_volume_call import ChangeVolume
from .join_group_call import JoinGroupCall
from .leave_group_call import LeaveGroupCall


class Groups(ChangeVolume, JoinGroupCall, LeaveGroupCall):
    pass
