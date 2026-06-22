from .clear_cache import ClearCache
from .clear_call import ClearCall
from .connect_call import ConnectCall
from .handle_connection_changed import HandleConnectionChanged
from .handle_emojis_update import HandleEmojisUpdate
from .handle_mtproto_updates import HandleMTProtoUpdates
from .handle_request_participants import HandleRequestParticipants
from .handle_stream_ended import HandleStreamEnded
from .handle_stream_frame import HandleStreamFrame
from .handle_subchain_request import HandleSubchainRequest
from .join_presentation import JoinPresentation
from .log_retries import LogRetries
from .request_broadcast_part import RequestBroadcastPart
from .request_broadcast_timestamp import RequestBroadcastTimestamp
from .switch_connection import SwitchConnection
from .update_sources import UpdateSources
from .update_status import UpdateStatus


class Internal(
    ClearCache,
    ClearCall,
    ConnectCall,
    HandleConnectionChanged,
    HandleEmojisUpdate,
    HandleMTProtoUpdates,
    HandleRequestParticipants,
    HandleStreamEnded,
    HandleStreamFrame,
    HandleSubchainRequest,
    JoinPresentation,
    LogRetries,
    RequestBroadcastPart,
    RequestBroadcastTimestamp,
    SwitchConnection,
    UpdateSources,
    UpdateStatus,
):
    pass
