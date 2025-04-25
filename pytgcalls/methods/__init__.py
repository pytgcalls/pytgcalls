from .calls import Calls
from .decorators import Decorators
from .internal import Internal
from .stream import StreamMethods
from .utilities import Utilities


class Methods(
    Calls,
    Decorators,
    Internal,
    StreamMethods,
    Utilities,
):
    pass
