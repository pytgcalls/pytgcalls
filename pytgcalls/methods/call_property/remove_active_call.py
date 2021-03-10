class RemoveActiveCall:
    def __init__(self, pytgcalls):
        self.pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def _remove_active_call(self, chat_id: int):
        if chat_id in self.pytgcalls._active_calls:
            del self.pytgcalls._active_calls[chat_id]
