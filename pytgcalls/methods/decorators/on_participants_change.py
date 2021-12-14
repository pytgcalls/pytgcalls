from typing import Callable

from ...scaffold import Scaffold


class OnParticipantsChange(Scaffold):
    def on_participants_change(self) -> Callable:
        """Decorator for handling when the participant
        list of a group call is changed

        When the participant list changes, this decorator
        will be raised

        Example:
            .. code-block:: python
                :emphasize-lines: 4-5

                ...
                app = PyTgCalls(client)
                ...
                @app.on_participants_change()
                async def handler(client: PyTgCalls, update: Update):
                    print(update)
                ...
                app.run()

        """

        method = 'PARTICIPANTS_LIST'

        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._on_event_update.add_handler(
                    method,
                    func,
                )
            return func
        return decorator
