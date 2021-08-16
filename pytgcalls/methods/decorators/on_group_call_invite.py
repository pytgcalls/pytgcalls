from typing import Callable

from ...scaffold import Scaffold


class OnGroupCallInvite(Scaffold):
    def on_group_call_invite(self) -> Callable:
        method = 'INVITE_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
