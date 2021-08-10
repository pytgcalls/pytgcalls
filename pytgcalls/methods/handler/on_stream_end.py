from typing import Callable


class OnStreamEnd:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    def on_stream_end(self) -> Callable:
        method = 'STREAM_END_HANDLER'

        # noinspection PyProtectedMember
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._pytgcalls._add_handler(
                    method, {
                        'callable': func,
                    },
                )
            return func
        return decorator
