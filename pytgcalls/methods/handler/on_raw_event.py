from typing import Callable


class OnRawUpdate:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    def on_raw_update(self) -> Callable:
        method = 'EVENT_UPDATE_HANDLER'

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
