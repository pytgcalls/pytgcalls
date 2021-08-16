from typing import Callable

from ...scaffold import Scaffold


class OnClosedVoiceChat(Scaffold):
    def on_closed_voice_chat(self) -> Callable:
        method = 'CLOSED_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
