from typing import Callable

from ...scaffold import Scaffold


class OnKicked(Scaffold):
    def on_kicked(self) -> Callable:
        """Decorator for handling when kicked
        from a group/channel

        When your userbot will be kicked from
        a group/channel, this decorator will be
        raised

        Example:
            .. code-block:: python
                :emphasize-lines: 4-5

                ...
                app = PyTgCalls(client)
                ...
                @app.on_kicked()
                async def handler(client: PyTgCalls, chat_id: int):
                    print(chat_id)
                ...
                app.run()

        """

        method = 'KICK_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
