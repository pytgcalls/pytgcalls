from typing import Callable

from deprecation import deprecated

from ...scaffold import Scaffold


class OnRawUpdate(Scaffold):

    @deprecated(
        deprecated_in='1.0.0.dev1',
        details='This method is no longer supported.',
    )
    def on_raw_update(self) -> Callable:
        pass
