from typing import Callable


class OnClosedVoiceChat:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    def on_closed_voice_chat(self) -> Callable:
        method = 'CLOSED_HANDLER'

        # noinspection PyProtectedMember
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self._pytgcalls._add_handler(
                    method, {
                        'callable': func,
                    },
                )
            return func
        return decorator
