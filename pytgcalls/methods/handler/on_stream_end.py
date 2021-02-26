from typing import Callable


class OnStreamEnd:
    def on_stream_end(self) -> callable:
        method = 'STREAM_END_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._add_handler(
                    method, {
                        'callable': func,
                    },
                )
            return func
        return decorator
