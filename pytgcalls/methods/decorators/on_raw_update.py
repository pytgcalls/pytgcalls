from typing import Callable

from ...scaffold import Scaffold


class OnRawUpdate(Scaffold):
    def on_raw_update(self) -> Callable:
        method = 'RAW_UPDATE_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
