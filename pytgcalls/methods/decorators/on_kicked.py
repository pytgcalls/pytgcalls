from typing import Callable

from ...scaffold import Scaffold


class OnKicked(Scaffold):
    def on_kicked(self) -> Callable:
        method = 'KICK_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
