from typing import Callable


class OnNoVoiceChat:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    def on_no_voice_chats(self) -> Callable:
        method = 'NO_VOICE_CHAT_HANDLER'

        # noinspection PyProtectedMember
        def decorator(func: Callable) -> Callable:
            if self is not None:
                self.pytgcalls._add_handler(
                    method, {
                        'callable': func,
                    },
                )
            return func
        return decorator
