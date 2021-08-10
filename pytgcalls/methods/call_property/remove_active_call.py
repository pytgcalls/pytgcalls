class RemoveActiveCall:
    def __init__(self, pytgcalls):
        self._pytgcalls = pytgcalls

    # noinspection PyProtectedMember
    def _remove_active_call(self, chat_id: int):
        if chat_id in self._pytgcalls._active_calls:
            del self._pytgcalls._active_calls[chat_id]
