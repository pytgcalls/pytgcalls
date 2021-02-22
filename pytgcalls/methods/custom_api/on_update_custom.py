from typing import Callable


class OnUpdateCustom:
    def on_update_custom_api(self: "....pytgcalls.PytgCalls" = None) -> callable:
        method = 'CUSTOM_API_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._add_handler(method, { # noqa
                    'callable': func
                })
            else:
                func.handler_pytgcalls = (
                    {
                        'callable': func
                    },
                    method
                )
            return func
        return decorator
