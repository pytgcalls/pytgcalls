from .clear_cache import ClearCache
from .clear_call import ClearCall
from .connect_call import ConnectCall
from .emit_sig_data import EmitSigData
from .handle_connection_changed import HandleConnectionChanged
from .handle_mtproto_updates import HandleMTProtoUpdates
from .handle_stream_ended import HandleStreamEnded
from .handle_stream_frame import HandleStreamFrame
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
    EmitSigData,
    HandleConnectionChanged,
    HandleMTProtoUpdates,
    HandleStreamEnded,
    HandleStreamFrame,
    JoinPresentation,
    LogRetries,
    RequestBroadcastPart,
    RequestBroadcastTimestamp,
    SwitchConnection,
    UpdateSources,
    UpdateStatus,
):
    pass
