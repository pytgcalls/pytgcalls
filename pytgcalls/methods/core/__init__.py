from .binding_runner import BindingRunner
from .set_video_call_status import SetVideoCallStatus


class Core(
    BindingRunner,
    SetVideoCallStatus,
):
    pass
