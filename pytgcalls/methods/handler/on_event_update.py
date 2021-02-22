from typing import Callable


class OnEventUpdate:
    def on_event_update(self: "....pytgcalls.PytgCalls" = None) -> callable:
        method = 'EVENT_UPDATE_HANDLER'

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
