from .calls import Calls
from .decorators import Decorators
from .stream import StreamMethods
from .utilities import Utilities


class Methods(
    Calls,
    Decorators,
    StreamMethods,
    Utilities,
):
    pass
