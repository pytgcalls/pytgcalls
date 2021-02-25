from typing import Callable


class OnStreamEnd:
    def on_stream_end(self: '....pytgcalls.PytgCalls' = None) -> callable:
        method = 'STREAM_END_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._add_handler(
                    method, {  # noqa
                        'callable': func,
                    },
                )
            else:
                func.handler_pytgcalls = (
                    {
                        'callable': func,
                    },
                    method,
                )
            return func

        return decorator
