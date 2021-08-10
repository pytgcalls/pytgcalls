from typing import Callable


class OnUpdateCustom:
    def __init__(self, custom_api):
        self._custom_api = custom_api

    def on_update_custom_api(self) -> Callable:
        # noinspection PyProtectedMember
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._custom_api._custom_api_handler = func
            return func
        return decorator
