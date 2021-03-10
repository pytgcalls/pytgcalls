class AddActiveCall:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def _add_active_call(self, chat_id: int):
        if chat_id not in self.pytgcalls._active_calls:
            self.pytgcalls._active_calls[chat_id] = 'playing'
