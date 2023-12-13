from .decorators import Decorators
from .groups import Groups
from .stream import StreamMethods
from .utilities import Utilities


class Methods(
    Decorators,
    Groups,
    StreamMethods,
    Utilities,
):
    pass
