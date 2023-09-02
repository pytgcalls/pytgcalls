from typing import Callable

import deprecation

from ... import __version__
from ...scaffold import Scaffold


class OnRawUpdate(Scaffold):

    @deprecation.deprecated(
        deprecated_in='1.0.0.dev1',
        removed_in='1.0.0.dev1',
        current_version=__version__,
        details='This method is no longer supported.',
    )
    def on_raw_update(self) -> Callable:
        pass
