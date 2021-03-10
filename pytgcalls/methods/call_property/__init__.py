from .active_calls import ActiveCalls
from .add_active_call import AddActiveCall
from .add_call import AddCall
from .calls import Calls
from .remove_active_call import RemoveActiveCall
from .remove_call import RemoveCall
from .set_status import SetStatus


class CallProperty(
    ActiveCalls,
    AddActiveCall,
    AddCall,
    Calls,
    RemoveActiveCall,
    RemoveCall,
    SetStatus,
):
    pass
