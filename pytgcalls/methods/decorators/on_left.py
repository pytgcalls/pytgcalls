from typing import Callable

from ...scaffold import Scaffold


class OnLeft(Scaffold):
    def on_left(self) -> Callable:
        """Decorator for handling when the userbot
        left a group/channel

        When your userbot leave a a group/channel,
        this decorator will be raised

        Example:
            .. code-block:: python
                :emphasize-lines: 4-5

                ...
                app = PyTgCalls(client)
                ...
                @app.on_left()
                async def handler(client: PyTgCalls, chat_id: int):
                    print(chat_id)
                ...
                app.run()

        """
        method = 'LEFT_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
