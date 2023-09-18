from .decorators import Decorators
from .groups import Groups
from .stream import Stream
from .utilities import Utilities


class Methods(
    Decorators,
    Groups,
    Stream,
    Utilities,
):
    pass
