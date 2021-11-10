from typing import Callable

from ...scaffold import Scaffold


class OnParticipantsChange(Scaffold):
    def on_participants_change(self) -> Callable:
        method = 'PARTICIPANTS_LIST'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
