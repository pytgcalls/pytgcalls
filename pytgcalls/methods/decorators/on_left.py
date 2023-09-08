from typing import Callable

from ...scaffold import Scaffold


class OnLeft(Scaffold):
    def on_left(self) -> Callable:
        method = 'LEFT_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
