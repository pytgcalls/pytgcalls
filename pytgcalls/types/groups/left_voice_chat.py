from ...types.update import Update


class LeftVoiceChat(Update):
    def __init__(
        self,
        chat_id: int,
    ):
        super().__init__(chat_id)

    def __str__(self):
        return 'LEFT_VOICE_CHAT'
