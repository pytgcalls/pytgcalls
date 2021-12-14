from typing import Callable

from ...scaffold import Scaffold


class OnClosedVoiceChat(Scaffold):
    def on_closed_voice_chat(self) -> Callable:
        """Decorator for handling closed voice chat event.

        When a video chat closes, this decorator will
        be raised

        Example:
            .. code-block:: python
                :emphasize-lines: 4-5

                ...
                app = PyTgCalls(client)
                ...
                @app.on_closed_voice_chat()
                async def handler(client: PyTgCalls, chat_id: int):
                    print(chat_id)
                ...
                app.run()

        """
        method = 'CLOSED_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
