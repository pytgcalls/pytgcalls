from typing import Callable


class OnUpdateCustom:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    def on_update_custom_api(self) -> Callable:
        method = 'CUSTOM_API_HANDLER'

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
