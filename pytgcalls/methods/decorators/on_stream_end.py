from typing import Callable

from ...scaffold import Scaffold


class OnStreamEnd(Scaffold):
    def on_stream_end(self) -> Callable:
        """Decorator for handling when a stream playing
        is ended

        When a streaming will end, this decorator will
        be raised

        Example:
            .. code-block:: python
                :emphasize-lines: 4-5

                ...
                app = PyTgCalls(client)
                ...
                @app.on_stream_end()
                async def handler(client: PyTgCalls, update: Update):
                    print(update)
                ...
                app.run()

        """

        method = 'STREAM_END_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
