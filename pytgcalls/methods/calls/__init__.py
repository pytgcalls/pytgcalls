from .change_volume_call import ChangeVolumeCall
from .delete_messages import DeleteMessages
from .delete_participant_messages import DeleteParticipantMessages
from .get_participants import GetParticipants
from .leave_call import LeaveCall
from .send_message import SendMessage


class Calls(
    ChangeVolumeCall,
    DeleteMessages,
    DeleteParticipantMessages,
    GetParticipants,
    LeaveCall,
    SendMessage,
):
    pass
