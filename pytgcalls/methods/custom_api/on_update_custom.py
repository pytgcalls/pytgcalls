from typing import Callable


class OnUpdateCustom:
    def on_update_custom_api(self) -> Callable:
        method = 'CUSTOM_API_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._add_handler(
                    method, {
                        'callable': func,
                    },
                )
            return func
        return decorator
