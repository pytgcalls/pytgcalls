from typing import Callable

from ...scaffold import Scaffold


class OnRawUpdate(Scaffold):
    def on_raw_update(self) -> Callable:
        """Decorator for handling raw update

        When a raw update will be received, this
        decorator will be raised

        Example:
            .. code-block:: python
                :emphasize-lines: 4-5

                ...
                app = PyTgCalls(client)
                ...
                @app.on_raw_update()
                async def handler(client: PyTgCalls, update: Update):
                    print(update)
                ...
                app.run()

        """

        method = 'RAW_UPDATE_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
