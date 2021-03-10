from typing import Callable


class OnKicked:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    def on_kicked(self) -> Callable:
        method = 'KICK_HANDLER'

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
