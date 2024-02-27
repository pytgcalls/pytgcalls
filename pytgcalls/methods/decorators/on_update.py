from typing import Callable

from ...scaffold import Scaffold


class OnUpdate(Scaffold):
    def on_update(self, filters=None) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self.add_handler(
                func,
                filters,
            )

        return decorator
