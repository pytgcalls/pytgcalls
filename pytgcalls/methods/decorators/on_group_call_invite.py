from typing import Callable

from ...scaffold import Scaffold


class OnGroupCallInvite(Scaffold):
    def on_group_call_invite(self) -> Callable:
        """Decorator for handling when invited
        from voice chat event.

        When your userbot will be invited on voice
        chat, this decorator will be raised

        Example:
            .. code-block:: python
                :emphasize-lines: 4-5

                ...
                app = PyTgCalls(client)
                ...
                @app.on_group_call_invite()
                async def handler(client: PyTgCalls, service_msg):
                    print(service_msg)
                ...
                app.run()

        """
        method = 'INVITE_HANDLER'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
