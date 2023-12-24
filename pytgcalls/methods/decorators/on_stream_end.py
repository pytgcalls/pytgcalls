from typing import Callable

from ...scaffold import Scaffold


class OnStreamEnd(Scaffold):
    def on_stream_end(self) -> Callable:
        method = 'STREAM_END_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
