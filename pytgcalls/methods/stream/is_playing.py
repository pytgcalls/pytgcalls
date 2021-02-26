class IsPlaying:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def is_playing(self, chat_id: int):
        if chat_id in self.pytgcalls._current_status_chats:
            return self.pytgcalls._current_status_chats[chat_id]
        else:
            raise Exception('NOT_IN_GROUP')
