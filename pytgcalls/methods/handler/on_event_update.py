from typing import Callable


class OnEventUpdate:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    def on_event_update(self) -> Callable:
        method = 'EVENT_UPDATE_HANDLER'

        # noinspection PyProtectedMember
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self.pytgcalls._add_handler(
                    method, {
                        'callable': func,
                    },
                )
            return func
        return decorator
