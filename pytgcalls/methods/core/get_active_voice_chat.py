class GetActiveVoiceChat:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def get_active_voice_chats(self):
        return self.pytgcalls._current_active_chats
